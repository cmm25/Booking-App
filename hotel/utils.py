import secrets
import logging
import base64
import requests
from django.core.mail import EmailMessage
from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from .models import User, OneTimePassword

# Initialize logger
logger = logging.getLogger(__name__)

def generate_otp():
    otp = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    logger.info(f"Generated OTP: {otp}")
    return otp

def sendOtpEmail(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        logger.error(f"User with email {email} does not exist")
        return False  # Handle the case where user does not exist

    otp = generate_otp()
    subject = "One-Time Passcode for Email Verification"
    current_site = settings.SITE_DOMAIN
    email_body = f"""
    Hi {user.first_name},

    Thanks for signing up on {current_site}. 
    Please verify your email with the following One-Time Passcode:

    {otp}

    This code will expire in 10 minutes.

    If you didn't request this code, please ignore this email.

    Best regards,
    The test Team
    """
    from_email = settings.DEFAULT_FROM_EMAIL

    OneTimePassword.objects.update_or_create(
        user=user,
        defaults={'code': otp}
    )

    try:
        send_email = EmailMessage(subject=subject, body=email_body, from_email=from_email, to=[email])
        send_email.send(fail_silently=False)
        logger.info(f"OTP email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")
        return False

def send_email(data):
    try:
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            to=[data['to_email']],
            from_email=settings.EMAIL_HOST_USER
        )
        email.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

class Google():
    @staticmethod
    def validate_google_token(token):
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            return idinfo
        except ValueError as e:
            raise AuthenticationFailed('Invalid token')

def login_social_user(email, password):
    user = authenticate(email=email, password=password)
    if user is None:
        raise AuthenticationFailed('Invalid credentials')
    user_tokens = user.tokens()
    return {
        'email': user.email,
        'full_name': user.get_full_name(),
        'access_token': str(user_tokens.get('access')),
        'refresh_token': str(user_tokens.get('refresh'))
    }

def register_social_user(provider, email, first_name, last_name):
    user = User.objects.filter(email=email)
    if user.exists():
        if provider == user[0].auth_provider:
           return login_social_user(email, settings.SOCIAL_AUTH_PASSWORD)
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
        register_user = User.objects.create_user(**new_user)
        register_user.auth_provider = provider
        register_user.is_verified = True
        register_user.save()
        return login_social_user(email=register_user.email, password=settings.SOCIAL_AUTH_PASSWORD)
