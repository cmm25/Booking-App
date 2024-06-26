import random
from django.core.mail import EmailMessage
from .models import User, OneTimePassword
from django.conf import settings
from google.auth.transport import requests
from google.oauth2 import id_token
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed

def generateOtp():
    OTP = ''.join([str(random.randint(1, 9)) for _ in range(6)])
    return OTP

def sendOtpEmail(email):
    otp = generateOtp()
    subject = "One time passcode for Email verification"

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return  # handle the case where user does not exist

    current_site = "your_site_domain.com"  # Set this to your site's domain
    email_body = f"Hi {user.first_name}, thanks for signing up on {current_site}. Please verify your email with the One Time Passcode: {otp}"
    from_email = settings.DEFAULT_FROM_EMAIL

    OneTimePassword.objects.create(user=user, code=otp)

    send_email = EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[email])
    send_email.send(fail_silently=True)


def send_email(data):
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        to=[data['to_email']],
        from_email= settings.EMAIL_HOST_USER
    )
    email.send()



class Google():
    @staticmethod
    def validate_google_token(token):
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            return idinfo
        except ValueError as e:
            raise AuthenticationFailed('Invalid token')

def login_social_user (email, password):
     user = authenticate(email = email, password = password)
     user_tokens = user.tokens()
     return {
            'email': user.email,
            'full_name': user.get_full_name(),
            'access_token':str( user_tokens.get('access')),
            'refresh_token': str(user_tokens.get('refresh'))
    }  

def register_social_user(provider, email, first_name, last_name):
    user = User.objects.filter(email = email)
    if user.exists():
        if provider == user[0].auth_provider:
           login_social_user(email, settings.SOCIAL_AUTH_PASSWORD)
        else:
            raise AuthenticationFailed(
                detail=f"Please continue login with {user[0].auth_provider}"
            )
    else:
        new_user = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': settings.SOCIAL_AUTH_PASSWORD
        }
        register_user = User.objects.create_user( **new_user)
        register_user.auth_provider = provider
        register_user.is_verified = True
        register_user.save()
        login_social_user(email = register_user.email,password = settings.SOCIAL_AUTH_PASSWORD)