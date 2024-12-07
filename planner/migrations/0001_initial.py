# Generated by Django 5.1.3 on 2024-12-01 10:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Planner",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("ordering_num", models.BigIntegerField(verbose_name="정렬 우선 순위")),
                ("title", models.CharField(max_length=255, verbose_name="제목")),
                (
                    "is_delete",
                    models.BooleanField(default=False, verbose_name="삭제 여부"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="플래너 생성일"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="플래너 수정일"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="planner",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="회원 식별 ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "플래너",
                "verbose_name_plural": "플래너들",
                "ordering": ["ordering_num"],
            },
        ),
    ]
