
from django.urls import path
from .views import RegisterView, VerifyOTPView, LoginView, ResendOTPView

urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register"
    ),
    path(
        "verify-otp/",
        VerifyOTPView.as_view(),
        name="verify_otp"
    ),
    path(
        "login/",
        LoginView.as_view(),
        name="login"
    ),
    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),

]
