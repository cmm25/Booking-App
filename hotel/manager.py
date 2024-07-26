from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email

class UserManager(BaseUserManager):
    def email_validator(self, email):
        """
        Validate the email address using Django's built-in validator.
        Raise ValueError if the email is invalid.
        """
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_('Invalid email address'))
        
    def create_user(self, email, first_name, last_name, password, **extra_fields):
        """
        Create and save a regular user with the given email, first name, last name, and password.
        """
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_('The Email field must be filled'))
        if not first_name:
            raise ValueError(_('The First Name field must be filled'))
        if not last_name:
            raise ValueError(_('The Last Name field must be filled'))
        
        # Create a new user instance
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        """
        Create and save a superuser with the given email, first name, last name, and password.
        """
        # Set default values for superuser fields
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        # Ensure the superuser has the necessary permissions
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Staff must be true to access admin'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must be true to access admin'))
        
        # Create the superuser using the create_user method
        user = self.create_user(email, first_name, last_name, password, **extra_fields)
        user.save(using=self._db)
        return user
