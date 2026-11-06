from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from .models import StudentProfile
import re

# CHANGE THIS TO YOUR COLLEGE EMAIL DOMAIN
COLLEGE_DOMAIN = "akgec.ac.in"


class RegisterSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    # REGISTRATION FIELDS

    section = serializers.CharField(max_length=20)

    year = serializers.ChoiceField(
        choices=[
            ("1st Year", "1st Year"),
            ("2nd Year", "2nd Year"),
            ("3rd Year", "3rd Year"),
            ("4th Year", "4th Year"),
        ]
    )

    residence = serializers.ChoiceField(
        choices=[
            ("Hosteller", "Hosteller"),
            ("Day Scholar", "Day Scholar"),
        ]
    )

    phone_no = serializers.CharField(max_length=10)
    roll_no = serializers.CharField(max_length=30)
    student_no = serializers.CharField(max_length=30)

    # NAME VALIDATION

    def validate_name(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Name is required."
            )

        if not re.fullmatch(r"[A-Za-z ]+", value):
            raise serializers.ValidationError(
                "Name can contain only letters and spaces."
            )

        return value

    # EMAIL VALIDATION

    def validate_email(self, value):

        value = value.lower().strip()

        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError(
                "Enter a valid email address."
            )

        domain = value.rsplit("@", 1)[-1]

        if domain != COLLEGE_DOMAIN.lower():
            raise serializers.ValidationError(
                "Use your official college email."
            )

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Email already registered."
            )

        return value

    # PASSWORD VALIDATION

    def validate_password(self, value):

        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must have atleast 8 characters."
            )

        return value

    # PHONE NUMBER VALIDATION

    def validate_phone_no(self, value):

        if not re.fullmatch(r"[0-9]{10}", value):
            raise serializers.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        return value

    # ROLL NUMBER VALIDATION

    def validate_roll_no(self, value):

        value = value.strip()

        if StudentProfile.objects.filter(
            roll_no__iexact=value
        ).exists():

            raise serializers.ValidationError(
                "Roll number already registered."
            )

        return value

    # STUDENT NUMBER VALIDATION

    def validate_student_no(self, value):

        value = value.strip()

        if StudentProfile.objects.filter(
            student_no__iexact=value
        ).exists():

            raise serializers.ValidationError(
                "Student number already registered."
            )

        return value
