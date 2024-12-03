from django.db import models

# Create your models here.


class Calendar(models.Model):
    id = models.BigAutoField(primary_key=True)
    planner_id = models.BigIntegerField()  # FK 를 직접 참조
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calendars"
