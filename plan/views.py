# plan/views.py
from typing import Any, Dict, List, cast

from django.shortcuts import render, redirect  # render 및 redirect 추가 (템플릿 렌더링 및 리다이렉트 용도)
from rest_framework import status  # HTTP 상태 코드 관리 모듈 추가
from rest_framework.permissions import IsAuthenticated  # 인증된 사용자만 접근 허용
from rest_framework.request import Request  # DRF의 Request 클래스를 임포트하여 응답 객체를 생성
from rest_framework.response import Response  # DRF의 Response 클래스를 임포트하여 응답 객체를 사용
from rest_framework.views import APIView  # APIView를 상속받아 HTTP 요청을 처리하는 뷰 클래스를 생성

from plan.models import Plan  # Plan 모델 임포트
from user.models import User  # User 모델 임포트

from .serializers import PlanSerializer  # PlanSerializer 임포트
from .services import PlanService  # PlanService 임포트
from datetime import datetime


class PlanListView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request: Request) -> Response:
        search_keyword = request.query_params.get("search")  # 검색 키워드 가져오기
        plans = PlanService.get_plans(cast(User, request.user), search_keyword)  # 사용자에 따른 계획 가져오기
        serializer = PlanSerializer(plans, many=True)  # 직렬화
        return render(request, 'plan.html', {'plans': serializer.data, 'current_year': datetime.now().year})  # 템플릿 렌더링


class PlanCreateView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def post(self, request: Request) -> Response:
        """새로운 계획을 생성하는 뷰"""
        plan_data = request.data  # 요청 데이터에서 계획 정보 추출
        plan = PlanService.create_plan(plan_data, cast(User, request.user))  # 계획 생성
        serializer = PlanSerializer(plan)  # 직렬화
        return Response(serializer.data, status=status.HTTP_201_CREATED)  # 생성된 계획 반환


class PlanUpdateView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def post(self, request: Request, plan_id: int) -> Response:
        """기존 계획을 업데이트하는 뷰"""
        try:
            updated_plan = PlanService.update_plan(
                plan_id, request.data, cast(User, request.user)
            )
            serializer = PlanSerializer(updated_plan)
            return Response(serializer.data)  # 업데이트된 계획 반환

        except Plan.DoesNotExist:
            return Response(
                {"error": "Plan not found"}, status=status.HTTP_404_NOT_FOUND
            )  # 계획이 존재하지 않을 경우 오류 메시지 반환
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )  # 기타 예외 발생 시 오류 메시지 반환


class PlanDeleteView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def delete(self, request: Request, plan_id: int) -> Response:
        """plan 삭제 (soft delete)"""
        try:
            PlanService.delete_plan(plan_id, cast(User, request.user))  # 계획 삭제
            return Response({"message": "Successfully deleted"})  # 삭제 성공 메시지 반환
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )  # 삭제 중 오류 발생 시 오류 메시지 반환
