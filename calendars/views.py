from typing import cast

from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from calendars.serializers import CalendarSerializer
from calendars.services import CalendarService
from user.models import User

from .models import Calendar

# Create your views here.


class CalendarListView(APIView):
    # 캘린더 조회 API
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        # 사용자의 모든 캘린더를 조회
        try:
            user = cast(User, request.user)
            calendars = CalendarService.get_calendars(user.id)
            serializer = CalendarSerializer(calendars, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalendarCreateView(APIView):
    # 캘린더 생성 API
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        # 새로운 캘린더 생성
        try:
            user = cast(User, request.user)
            calendar = CalendarService.create_calendar(user.id)
            serializer = CalendarSerializer(calendar)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CalendarUpdateView(APIView):
    # 캘린더 수정 API
    permission_classes = [IsAuthenticated]

    def put(self, request: Request, calendar_id: int) -> Response:
        # 캘린더 정보 수정
        try:
            user = cast(User, request.user)
            calendar = CalendarService.update_calendar(
                calendar_id=calendar_id, planner_id=user.id, data=request.data
            )
            serializer = CalendarSerializer(calendar)
            return Response(serializer.data)

        except Calendar.DoesNotExist:
            return Response(
                {"error": "Calendar not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CalendarDeleteView(APIView):
    # 캘린더 삭제 API (soft delete)
    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, calendar_id: int) -> Response:
        # 캘린더 삭제
        try:
            user = cast(User, request.user)
            CalendarService.delete_calendar(calendar_id, user.id)
            return Response({"message": "Successfully deleted"})

        except Calendar.DoesNotExist:
            return Response(
                {"error": "Calendar not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
