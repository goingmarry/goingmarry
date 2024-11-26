from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("signup/", views.UserSignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("deactivate/", views.UserDeactivateView.as_view(), name="deactivate"),
    # 이메일 인증
    path(
        "verify/send/", views.SendVerificationView.as_view(), name="send-verification"
    ),
    path("verify/confirm/", views.VerifyCodeView.as_view(), name="verify-code"),
]
