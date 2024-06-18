import random
from django.core.mail import EmailMessage
from .models import User, OneTimePassword
from django.conf import settings

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