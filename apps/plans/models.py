from django.db import models

# Create your models here.


class Plan(models.Model):
    id = models.BigAutoField(primary_key=True)
    planner_id = models.BigIntegerField()  # FK 대신 임시로 BigIntegerField 사용
    ordering_num = models.BigIntegerField()
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
