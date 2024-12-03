from django.conf import settings
from django.db import models


class Planner(models.Model):
    id = models.BigAutoField(primary_key=True)  # Auto-incrementing primary key
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="planner",
        verbose_name="회원 식별 ID",
    )
    ordering_num = models.BigIntegerField(verbose_name="정렬 우선 순위")  # Not null
    title = models.CharField(max_length=255, verbose_name="제목")  # Not null
    is_delete = models.BooleanField(
        default=False, verbose_name="삭제 여부"
    )  # Default false
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="플래너 생성일"
    )  # Not null
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="플래너 수정일"
    )  # Not null

    class Meta:
        ordering = ["ordering_num"]  # 정렬 우선 순위에 따라 정렬
        verbose_name = "플래너"
        verbose_name_plural = "플래너들"

    def __str__(self) -> str:
        return self.title
