from typing import Any, Dict

from django.db.models import QuerySet

from .models import Calendar


class CalendarService:
    @staticmethod
    def get_calendars(planner_id: int) -> QuerySet[Calendar]:
        # 캘린더 조회
        return Calendar.objects.filter(
            planner_id=planner_id, is_deleted=False
        ).order_by("-created_at")

    @staticmethod
    def create_calendar(planner_id: int) -> Calendar:
        # 캘린더 생성
        # Args : planner_id: Calendar 를 생성하는 Planner의 ID
        # Return : 생성된 Calendar 객체
        return Calendar.objects.create(planner_id=planner_id)

    @staticmethod
    def update_calendar(
        calendar_id: int, planner_id: int, data: Dict[str, Any]
    ) -> Calendar:

        # 캘린더 수정
        # Args :
        # - calendar_id : 수정할 Calendar의 ID
        # - planner_id : Calendar 소유자의 ID
        # - data : 수정할 데이터

        # Returns:
        # - 수정된 Calendar 객체

        # Raises:
        # - Calendar.DoesNotExist : Calendar를 찾을 수 없는 경우
        # - PermissionError : Calendar 소유자가 아닌 경우

        calendar = Calendar.objects.get(id=calendar_id, is_deleted=False)

        if calendar.planner_id != planner_id:
            raise PermissionError("Not authorized to update this calendar")

        for key, value in data.items():
            if hasattr(calendar, key):
                setattr(calendar, key, value)

        calendar.save()
        return calendar

    @staticmethod
    def delete_calendar(calendar_id: int, planner_id: int) -> bool:
        # 캘린더 삭제 (soft delete)
        # Args :
        # - calendar_id : 삭제할 Calendar의 ID
        # - planner_id : Calendar 소유자의 ID

        # Returns :
        # - 삭제 성공 여부

        # Raises :
        # - Calendar.DoesNotExist : Calendar를 찾을 수 없는 경우
        # - PermissionError : Calendar 소유자가 아닌 경우

        calendar = Calendar.objects.get(id=calendar_id, is_deleted=False)

        if calendar.planner_id != planner_id:
            raise PermissionError("Not authorized to delete this calendar")

        calendar.is_deleted = True
        calendar.save()
        return True
