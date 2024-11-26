from django.db import models

from apps.users.models import User

# Create your models here.


class Login(models.Model):
    login_id = models.BigAutoField(primary_key=True)
    user_num = models.ForeignKey(User, on_delete=models.CASCADE)
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    user_ip = models.CharField(max_length=50)
    user_agent = models.TextField()
    is_successful = models.BooleanField(default=True)
