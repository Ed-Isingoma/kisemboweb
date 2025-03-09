import uuid
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import json
from .models import Account, Session, Topic, TopicVideo, Subscription

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