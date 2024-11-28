from typing import Any, Optional, Tuple, Type

# django의 관리자 인터페이스를 구성하기 위한 admin 모듈을 가져옴
from django.contrib import admin

# 기본 제공되는 UserAdmin 클래스에서 사용자 관리 기능을 확장하기 위해 가져옴
from django.contrib.auth.admin import UserAdmin

# django의 http 요청 객체로, 관리자 인터페이스에서 http 요청을 처리할 때 사용할 수 있음
from django.http import HttpRequest

from .models import User


# @admin.register(User) : User모델을 Django 관리자 페이지에 등록
# 이 데이코레이터를 사용하면 클래스를 수동으로 등록할 필요가 없다
@admin.register(User)
# 최후의 수단으로 타입 이그노어...
# UserAdmin을 상속받아 사용자 관리를 위한 커스텀 관리자 클래스를 정의
class CustomUserAdmin(UserAdmin):  # type: ignore
    # 이 클래스에서 사용할 모델을 User로 설정
    model = User

    # 관리자 인터페이스에서 목록을 표시할 필드를 정의
    list_display = ("user_id", "email", "nickname", "is_active", "created_at")

    # 관리자 페이지의 우측 필터를 추가
    list_filter = ("is_active", "created_at")

    # 관리자 인터페이스의 검색창에서 검색 가능한 필드를 정의
    search_fields = ("user_id", "email", "nickname")

    # 목록의 기본 정렬 순서를 설정. 최신 생성 날짜 기준으로.
    ordering = ("-created_at",)

    # 사용자 세부 정보를 표시할 필드 그룹을 정의
    fieldsets = (
        # [기본 정보] 섹션에서 나오는 필드
        (None, {"fields": ("user_id", "password")}),
        # [개인 정보] 섹션에 나오는 필드]
        ("Personal info", {"fields": ("nickname", "email", "gender")}),
        # [권한] 섹션에 활성 상태 및 관리자 권한 관련 필드를 표시]
        # is_staff / is_superuser 는 차이가 있음
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        # [중요 날짜] 섹션에 마지막 로그인 시간, 생성일, 수정일 필드를 표시
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    # 새 사용자 추가 시 표시할 필드 그룹을 정의
    add_fieldsets = (
        (
            None,
            {
                # "wide" 클래스는 입력 필드를 넓게 표시하도록 CSS를 설정한다.
                "classes": ("wide",),
                # 새 사용자 추가 양식에 표시할 필드를 정의
                "fields": ("user_id", "password1", "password2", "nickname", "email"),
            },
        ),
    )

    # created_at, updated_at 필드를 읽기 전용으로 설정
    # 관리자 인터페이스에서 이 필드는 편집할 수 없으며, 데이터베이스의 값만 표시
    readonly_fields = ("created_at", "updated_at")
