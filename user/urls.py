from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("deactivate/", views.UserDeactivateView.as_view(), name="deactivate"),
    path("token/refresh/", views.TokenRefreshView.as_view(), name="token-refresh"),
]


# path(
#     "verify/send/", views.SendVerificationView.as_view(), name="send-verification"
# ),
# path("verify/confirm/", views.VerifyCodeView.as_view(), name="verify-code"),
# path("nickname/", views.NicknameUpdateView.as_view(), name="update-nickname"),
