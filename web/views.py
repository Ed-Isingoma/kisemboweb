import uuid
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import json
from .models import Account, Session, Topic, TopicVideo, Subscription
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests

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
                'duration_amount': int(data.get('duration_amount')),
                'mobile_number': data.get('mobile_number'),
                'total_price': float(data.get('total_price'))
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
            elif subscription_data['duration_unit'] == 'weekly':
                expiry = now + timedelta(weeks=subscription_data['duration_amount'])
            elif subscription_data['duration_unit'] == 'monthly':
                naive_expiry = timezone.make_naive(now) + relativedelta(months=+subscription_data['duration_amount'])
                expiry = timezone.make_aware(naive_expiry)

            subscription = Subscription.objects.create(
                userID=user,
                topicID=topic,
                expiry=expiry,
                confirmed=False
            )

            tx_ref = str(subscription.id)
            package = {
                "tx_ref": tx_ref,
                "amount": int(subscription_data['total_price']),
                "currency": "UGX",
                "email": user.email,
                "phone_number": '+256' + subscription_data['mobile_number'][1:],
                "redirect_url": "https://kisembopaymentstransit.vercel.app/"
            }

            headers = {
                'Authorization': f'Bearer {settings.FLW_SECRET_KEY}',
                'Content-Type': 'application/json'
            }

            print('and here we go to flwave:')
            print(headers)
            
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
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def generate_session_token():
    return str(uuid.uuid4())

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(email, code):
    send_mail(
        'Verification Code',
        f'Your verification code is: {code}',
        settings.EMAIL_HOST_USER,  # Uses the email from settings.py
        [email],
        fail_silently=False,
    )

def home_view(request):
    session_id = request.COOKIES.get('sessionId')
    user_id = request.COOKIES.get('userId')
    
    context = {
        'topics': Topic.objects.all(),
        'is_authenticated': False,
        'login_required': False,  # Ensure these keys exist in context
        'subscription_needed': False
    }
    
    if session_id and user_id:
        try:
            session = Session.objects.get(
                sessionID=session_id, 
                userID=user_id, 
                expiry__gt=timezone.now()
            )
            context['is_authenticated'] = True
            context['user_subscriptions'] = Subscription.objects.filter(
                userID=session.userID, 
                expiry__gt=timezone.now()
            )
        except Session.DoesNotExist:
            pass
    
    tea = request.GET.get('tea')
    sugar = request.GET.get('sugar')
    
    if tea:
        try:
            topic = Topic.objects.get(topicName=tea)
            context['topic_videos'] = TopicVideo.objects.filter(topicID=topic)
            
            if sugar:
                video = TopicVideo.objects.get(videoName=sugar)
                
                if context['is_authenticated']:
                    has_subscription = Subscription.objects.filter(
                        userID_id=session.userID.pk, 
                        topicID_id=topic.pk, 
                        expiry__gt=timezone.now()
                    ).exists() 

                    if has_subscription:
                        context['video_link'] = video.videoLink
                    else:
                        context['subscription_needed'] = True
                else:
                    context['login_required'] = True
        except (Topic.DoesNotExist, TopicVideo.DoesNotExist):
            pass  # Avoids errors if topic or video doesn't exist

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
	session_id = request.COOKIES.get('sessionId')
	print('logging out')
	if session_id:
		Session.objects.filter(sessionID=session_id).delete()
		response = JsonResponse({'success': True})
		response.delete_cookie('sessionId')
		response.delete_cookie('userId')
		return response
	return JsonResponse({'success': False, 'message': 'No active session found'})

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
            return JsonResponse({'success': True})
        except Account.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Invalid verification code'})

def change_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            account = Account.objects.get(email=email)
            verification_code = generate_verification_code()
            account.code = verification_code
            account.save()
            
            send_verification_email(email, verification_code)
            return JsonResponse({'success': True})
        except Account.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Email not found'})

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