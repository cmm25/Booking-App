import random
from django.core.mail import EmailMessage
from .models import User, OneTimePassword
from django.conf import settings


#KNOW HOW TO USE PYOTP
def generateOtp():
    OTP = ''
    for i in range(6):
        OTP += str(random.randint(1, 9)) 
    return OTP 

def sendOtpEmail(email):
    otp = generateOtp()
    Subject = "One time passcode for Email verification"
    print(otp)

    user= User.objects.get(email=email)
    current_site = ""
    email_body = f"Hi{user.first_name} thanks fpr signing up on
    {current_site} please verify your email with the \n One Time Passcode{otp}"
    from_email = settings.DEFAULT_FROM_EMAIL

    OneTimePassword.objects.create(user=user, code = otp)

    send_email=EmailMessage(subject=Subject, body=email_body, from_email=from_email
                            ,to=[email])
    send_email.send(fail_silently=True)