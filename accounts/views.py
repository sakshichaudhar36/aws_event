
import secrets
import uuid

from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils.text import slugify

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import StudentProfile, EmailOTP
from .serializers import RegisterSerializer


# --------------------------------------------------
# REGISTER API
# --------------------------------------------------

class RegisterView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        otp = str(secrets.randbelow(900000) + 100000)

        # Generate an internal unique username from the name
        username_base = slugify(data["name"])[:140] or "student"
        username = f"{username_base}_{uuid.uuid4().hex[:8]}"

        try:

            with transaction.atomic():

                user = User.objects.create_user(
                    username=username,
                    email=data["email"],
                    password=data["password"],
                    is_active=False
                )

                # Save student details
                StudentProfile.objects.create(
                    user=user,
                    name=data["name"],
                    section=data["section"],
                    year=data["year"],
                    residence=data["residence"],
                    phone_no=data["phone_no"],
                    roll_no=data["roll_no"],
                    student_no=data["student_no"],
                    is_email_verified=False
                )

                # Save OTP
                EmailOTP.objects.create(
                    user=user,
                    otp=otp,
                    expires_at=timezone.now()
                    + timedelta(minutes=1)
                )

                # Send OTP email
                send_mail(
                    subject="Society Event Email Verification",
                    message=(
                        f"Hello {data['name']},\n\n"
                        f"Your OTP is {otp}.\n"
                        "It expires in 1 minute."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False
                )

        except Exception as e:

            return Response(
                {
                    "error": "Registration failed. "
                    "Check SMTP configuration.",
                    "details": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "message": "OTP sent successfully.",
                "name": data["name"],
                "email": user.email
            },
            status=status.HTTP_201_CREATED
        )


# --------------------------------------------------
# VERIFY OTP API
# --------------------------------------------------

class VerifyOTPView(APIView):

    def post(self, request):

        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:

            return Response(
                {
                    "error": "Email and OTP are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            user = User.objects.get(
                email__iexact=email
            )

            otp_record = EmailOTP.objects.filter(
                user=user
            ).latest("created_at")

        except (User.DoesNotExist, EmailOTP.DoesNotExist):

            return Response(
                {
                    "error": "Invalid email or OTP."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_record.expires_at < timezone.now():

            return Response(
                {
                    "error": "OTP has expired. Please request a new OTP."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_record.otp != otp:

            return Response(
                {
                    "error": "Incorrect OTP."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        profile = StudentProfile.objects.get(
            user=user
        )

        profile.is_email_verified = True
        profile.save()

        user.is_active = True
        user.save()

        EmailOTP.objects.filter(
            user=user
        ).delete()

        return Response(
            {
                "message": "Email verified successfully. "
                "Your account is activated."
            },
            status=status.HTTP_200_OK
        )


# --------------------------------------------------
# RESEND OTP API
# --------------------------------------------------

class ResendOTPView(APIView):

    def post(self, request):

        email = request.data.get("email")

        if not email:

            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            user = User.objects.get(
                email__iexact=email
            )

        except User.DoesNotExist:

            return Response(
                {"error": "User not found. Please register first."},
                status=status.HTTP_404_NOT_FOUND
            )

        profile = StudentProfile.objects.filter(
            user=user
        ).first()

        if profile and profile.is_email_verified:

            return Response(
                {"message": "Email is already verified. Please login."},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp = str(secrets.randbelow(900000) + 100000)

        try:

            with transaction.atomic():

                EmailOTP.objects.filter(
                    user=user
                ).delete()

                EmailOTP.objects.create(
                    user=user,
                    otp=otp,
                    expires_at=timezone.now()
                    + timedelta(minutes=1)
                )

                send_mail(
                    subject="Society Event Email Verification",
                    message=(
                        f"Hello {profile.name if profile else user.username},\n\n"
                        f"Your new OTP is {otp}.\n"
                        "It expires in 1 minute."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False
                )

        except Exception:

            return Response(
                {
                    "error": "Unable to send OTP. Please try again later."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "message": "A new OTP has been sent to your registered email."
            },
            status=status.HTTP_200_OK
        )


# --------------------------------------------------
# LOGIN API
# --------------------------------------------------

class LoginView(APIView):

    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:

            return Response(
                {
                    "error": "Email and password are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            user_obj = User.objects.get(
                email__iexact=email
            )

        except User.DoesNotExist:

            return Response(
                {
                    "error": "Invalid email or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = authenticate(
            username=user_obj.username,
            password=password
        )

        if user is None:

            return Response(
                {
                    "error": "Invalid email or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:

            return Response(
                {
                    "error": "Please verify your college email first."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        token, created = Token.objects.get_or_create(
            user=user
        )

        profile = StudentProfile.objects.get(
            user=user
        )

        return Response(
            {
                "message": "Login successful.",
                "name": profile.name,
                "email": user.email,
                "token": token.key
            },
            status=status.HTTP_200_OK
        )