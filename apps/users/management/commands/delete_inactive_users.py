from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.users.models import User


class Command(BaseCommand):
    help = "60일 이상 비활성화된 회원 데이터 삭제"

    def handle(self, *args: tuple[str, ...], **kwargs: dict[str, Any]) -> None:
        # 60일 전 날짜 계산
        deletion_date = timezone.now() - timedelta(days=60)

        # is_active=False이고 updated_at이 60일 이전인 유저 조회
        users = User.objects.filter(is_active=False, updated_at__lte=deletion_date)

        # 삭제된 유저 수 카운트
        count = users.count()

        # 유저 삭제
        users.delete()

        self.stdout.write(
            self.style.SUCCESS(f"Successfully deleted {count} inactive users")
        )
