from django.db import models

from apps.users.models import User


class Login(models.Model):
    login_id = models.BigAutoField(primary_key=True)
    user_num = models.ForeignKey(User, on_delete=models.CASCADE)
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(
        null=True, blank=True
    )  # auto_now_add 제거, null/blank 허용
    user_ip = models.CharField(max_length=50)
    user_agent = models.TextField()
    is_success = models.BooleanField(default=True)  # is_successful -> is_success로 통일

    class Meta:
        db_table = "logins"  # 테이블 이름 명시적 지정 (선택사항)
