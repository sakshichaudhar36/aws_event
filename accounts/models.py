from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    # NEW STUDENT DETAILS

    name = models.CharField(max_length=100)

    section = models.CharField(max_length=20)

    YEAR_CHOICES = [
        ("1st Year", "1st Year"),
        ("2nd Year", "2nd Year"),
        ("3rd Year", "3rd Year"),
        ("4th Year", "4th Year"),
    ]

    year = models.CharField(
        max_length=20,
        choices=YEAR_CHOICES
    )

    RESIDENCE_CHOICES = [
        ("Hosteller", "Hosteller"),
        ("Day Scholar", "Day Scholar"),
    ]

    residence = models.CharField(
        max_length=20,
        choices=RESIDENCE_CHOICES
    )

    phone_no = models.CharField(max_length=10)

    roll_no = models.CharField(
        max_length=30,
        unique=True
    )

    student_no = models.CharField(
        max_length=30,
        unique=True
    )

    # EXISTING EMAIL VERIFICATION FIELD

    is_email_verified = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.user.username


class EmailOTP(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    def __str__(self):
        return f"OTP for {self.user.username}"