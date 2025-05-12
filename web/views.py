import uuid
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import os
import json
from .models import Account, Session, Topic, TopicVideo, Subscription
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def subscribe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')

            if not user_id:
                return JsonResponse({'error': 'User ID required'}, status=400)
            try:
                user = Account.objects.get(id=user_id)
            except Account.DoesNotExist:
                return JsonResponse({'error': 'Invalid user'}, status=400)

            subscription_data = {
                'topic_id': data.get('topic_id'),
                'duration_unit': data.get('duration_unit'),
                'duration_amount': data.get('duration_amount'),
                'mobile_number': data.get('mobile_number'),
            }

            if not all(subscription_data.values()):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            try:
                topic = Topic.objects.get(id=subscription_data['topic_id'])
            except Topic.DoesNotExist:
                return JsonResponse({'error': 'Invalid topic'}, status=400)

            now = timezone.now()
            if subscription_data['duration_unit'] == 'daily':
                expiry = now + timedelta(days=subscription_data['duration_amount'])
                total_price = subscription_data['duration_amount'] * topic.dailyPrice
            elif subscription_data['duration_unit'] == 'weekly':
                expiry = now + timedelta(weeks=subscription_data['duration_amount'])
                total_price = subscription_data['duration_amount'] * topic.weeklyPrice
            elif subscription_data['duration_unit'] == 'monthly':
                naive_expiry = timezone.make_naive(now) + relativedelta(months=+subscription_data['duration_amount'])
                expiry = timezone.make_aware(naive_expiry)
                total_price = subscription_data['duration_amount'] * topic.monthlyPrice

            subscription = Subscription.objects.create(
                userID=user,
                topicID=topic,
                expiry=expiry,
                confirmed=False
            )

            tx_ref = str(subscription.id)
            package = {
                "tx_ref": tx_ref,
                "amount": int(total_price),
                "currency": "UGX",
                "email": user.email,
                "phone_number": '+256' + subscription_data['mobile_number'][1:],
                "redirect_url": "https://www.kisemboacademy.com"
            }
            
            headers = {
                'Authorization': f'Bearer {settings.FLW_SECRET_KEY}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://api.flutterwave.com/v3/charges?type=mobile_money_uganda',
                headers=headers,
                json=package
            )

            if response.status_code == 200:
                flutterwave_response = response.json()
                if flutterwave_response.get('status') == 'success':
                    return JsonResponse({
                        'redirect': flutterwave_response['meta']['authorization']['redirect']
                    })
                else:
                    return JsonResponse({'error': flutterwave_response.get('message')}, status=400)

            return JsonResponse({'error': 'Payment gateway error'}, status=500)

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def generate_session_token():
    return str(uuid.uuid4())

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email, code):
    send_mail(
        'Kisembo Academy Verification Code',
        f'Thank you for signing up on Kisembo Academy. Your verification code is: {code}',
        settings.EMAIL_HOST_USER,  # Uses the email from settings.py
        [email],
        fail_silently=False,
    ) 

def home_view(request):
    topics = Topic.objects.prefetch_related('topicvideo_set').all()
    context = {
        'topics': [
            {
                'id': topic.id,
                'topicName': topic.topicName,
                'dailyPrice': topic.dailyPrice,
                'weeklyPrice': topic.weeklyPrice,
                'monthlyPrice': topic.monthlyPrice,
                'videos': [
                    {
                        'id': video.id, 
                        'videoName': video.videoName
                    }
                    for video in topic.topicvideo_set.all()
                ]
            }
            for topic in topics
        ],
        'is_authenticated': False,
        'user': None,
        'user_subscriptions': None,
        'login_required': False,
        'subscription_needed': False
    }

    session_id = request.COOKIES.get('sessionId')
    user_id = request.COOKIES.get('userId')

    if session_id and user_id:
        try:
            session = Session.objects.select_related('userID').get(
                sessionID=session_id,
                userID=user_id,
                expiry__gt=timezone.now()
            )
            user = session.userID
            context.update({
                'is_authenticated': True,
                'user': {'id': user.id, 'name': user.name},
                'user_subscriptions': Subscription.objects.filter(
                    userID=user,
                    expiry__gt=timezone.now(),
                    confirmed=True
                )
            })
        except Session.DoesNotExist:
            pass

    sugar = request.GET.get('sugar')

    if sugar:
        try:
            video = TopicVideo.objects.select_related('topicID').get(id=sugar)
            topic = video.topicID

            context['location_topic'] = topic.topicName
            context['location_video'] = video.videoName
            context['topic_videos'] = TopicVideo.objects.filter(topicID=topic)
            # the video links are being sent herein. maybe disable that later

            if context['is_authenticated']:
                has_subscription = Subscription.objects.filter(
                    userID_id=user.id,
                    topicID_id=topic.id,
                    expiry__gt=timezone.now(),
                    confirmed=True
                ).exists()

                if has_subscription:
                    context['video_link'] = video.videoLink
                else:
                    context['subscription_needed'] = True
            else:
                context['login_required'] = True

        except TopicVideo.DoesNotExist:
            pass  # Invalid video ID, ignore 
    
    if not request.GET:
        context['picked_videos'] = TopicVideo.objects.order_by('?')[:20]
        # the video links are being sent herein. maybe disable that later

    return render(request, 'home.html', context)

def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            account = Account.objects.get(email=email)
            if account.check_password(password) and account.is_confirmed:
                session_id = generate_session_token()
                Session.objects.create(
                    sessionID=session_id,
                    userID=account,
                    expiry=timezone.now() + timezone.timedelta(days=1)
                )
                
                response = JsonResponse({'success': True})
                response.set_cookie('sessionId', session_id, httponly=True)
                response.set_cookie('userId', account.id, httponly=True)
                return response
            else:
                return JsonResponse({'success': False, 'message': 'Invalid credentials'})
        except (Account.DoesNotExist, json.JSONDecodeError):
            return JsonResponse({'success': False, 'message': 'Invalid credentials or request format'})

def logout_view(request):
    response = JsonResponse({'success': True})
    
    session_id = request.COOKIES.get('sessionId')
    if session_id:
        Session.objects.filter(sessionID=session_id).delete()
    
    cookie_settings = {
        'path': '/',
        'samesite': 'Lax',
        'httponly': True
    }
    
    response.delete_cookie('sessionId', **cookie_settings)
    response.delete_cookie('userId', **cookie_settings)
    
    return response

def signup_view(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')

            if Account.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Email already registered'})

            verification_code = generate_verification_code()
            account = Account.objects.create(
                name=name,
                email=email,
                code=verification_code,
                is_confirmed=False
            )
            account.set_password(password)
            account.save()

            send_verification_email(email, verification_code)

            return JsonResponse({'success': True})
        except Exception as e:
            print("Signup error:", e)
            return JsonResponse({'success': False, 'message': 'An error occurred during signup.'})

def verify_account_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        
        try:
            account = Account.objects.get(email=email, code=code)
            account.is_confirmed = True
            account.code = None
            account.save()

            session_id = generate_session_token()
            Session.objects.create(
                sessionID=session_id,
                userID=account,
                expiry=timezone.now() + timezone.timedelta(days=1)
            )

            Subscription.objects.create(
                userID=account,
                topicID=Topic.objects.get(id=1),
                expiry=timezone.now() + relativedelta(days=30),
                confirmed=True
            )

            response = JsonResponse({'success': True})
            response.set_cookie('sessionId', session_id, httponly=True)
            response.set_cookie('userId', account.id, httponly=True)
            return response
        except Account.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid verification code'})

# def change_password_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
        
#         try:
#             account = Account.objects.get(email=email)
#             verification_code = generate_verification_code()
#             account.code = verification_code
#             account.save()
            
#             send_verification_email(email, verification_code)
#             return JsonResponse({'success': True})
#         except Account.DoesNotExist:
#             return JsonResponse({'success': False, 'message': 'Email not found'})

def reset_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        
        try:
            account = Account.objects.get(email=email, code=code)
            account.set_password(new_password)
            account.code = None
            account.save()
            return JsonResponse({'success': True})
        except Account.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid verification code'})


@csrf_exempt
@require_POST  # Allow only POST requests
def afterbill(request):
    try:
        verif_hash = request.headers.get("verif-hash")
        secret_hash = settings.FLW_SECRET_HASH

        if verif_hash != secret_hash:
            return JsonResponse({"error": "Hash values do not match"}, status=403)

        data = json.loads(request.body).get("data")
        if data.get("status") == "successful":
            tx_ref = data.get("tx_ref")
            subscription = Subscription.objects.get(id=tx_ref)
            subscription.confirmed = True
            subscription.save()

            return JsonResponse({"message": "Subscription confirmed", "tx_ref": tx_ref}, status=200)

        return JsonResponse({"message": "Transaction not successful"}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Subscription.DoesNotExist:
        return JsonResponse({"error": "Subscription not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


