from django.db import models
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


def validate_uzbek_phone_number(value):
    # Remove any non-digit characters from the phone number
    cleaned_number = ''.join(filter(str.isdigit, value))

    # Check if the cleaned number is of valid length for Uzbekistan
    if len(cleaned_number) != 12:
        raise ValidationError("Uzbek phone numbers must be 9 digits long")

    # Check if the cleaned number starts with the correct prefix for Uzbekistan
    if not cleaned_number.startswith('998'):
        raise ValidationError("Uzbek phone numbers must start with '998'")


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    founder = models.CharField(max_length=200)
    phoneNumber = models.CharField(max_length=13, validators=[validate_uzbek_phone_number])
    companyName = models.CharField(max_length=200, unique=True)

    twilioToken = models.CharField(max_length=400)
    twilioSid = models.CharField(max_length=400)
    twilioNumber = models.CharField(max_length=200)


class Customer(models.Model):

    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    fullName = models.CharField(max_length=200)

    phoneNumber = models.CharField(max_length=13, validators=[validate_uzbek_phone_number])
    info = models.TextField(null=True, blank=True)














