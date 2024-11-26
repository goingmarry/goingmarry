from typing import Any, Dict

from django.contrib.auth import authenticate  # 유저 인증을 처리하는 함수
from django.contrib.auth.hashers import (
    make_password,
)  # 패스워드를 해싱(암호화)하는 함수
from rest_framework import serializers  # DRF에서 제공하는 직렬화(Serializer) 도구

# JWT를 처리하는 기본 직렬화 도구
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


# 닉네임 업데이트용 Serializer 클래스
class NicknameUpdateSerializer(serializers.ModelSerializer[User]):
    class Meta:
        # User 모델을 사용
        model = User
        # 업데이트할 필드로 닉네임만 허용
        fields = ["nickname"]


# 이메일 인증 코드를 처리하기 위한 Serializer 클래스
class VerificationSerializer(serializers.Serializer[Any]):
    # verification_code라는 이름의 문자열 필드 정의, 최대 길이는 6자
    verification_code = serializers.CharField(max_length=6)


# JWT 인증 시 사용자 정보를 검증하고 토큰을 반환하는 Custom Serializer
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        # attrs는 요청에서 전달된 데이터를 포함하는 딕셔너리
        # 요청 데이터에서 user_id 추출
        user_id = attrs.get("user_id")
        # 요청 데이터에서 password 추출
        password = attrs.get("password")

        # user_id와 password가 모두 제공되었는지 확인
        if user_id and password:
            # Django의 authenticate 함수를 사용해 사용자 인증
            user = authenticate(
                username=user_id, password=password
            )  # user_id를 username으로 변경하여 사용

            # 인증 실패 시 예외 발생
            if not user:
                raise serializers.ValidationError(
                    "No active account found with the given credentials"
                    # 제공된 정보로 활성화된 계정을 찾을 수 없다는 메시지 반환
                )

            # 사용자 계정이 비활성화 상태인 경우 예외 발생
            if not user.is_active:
                raise serializers.ValidationError("This account is inactive")

            # 성공적으로 인증되었으면 username 필드를 설정하여 부모 클래스의 validate를 호출
            attrs["username"] = user_id
            # 부모 클래스의 검증 로직 실행 및 결과 반환
            return super().validate(attrs)
        else:
            # user_id나 password가 누락된 경우 예외 발생
            raise serializers.ValidationError('Must include "user_id" and "password".')


# 사용자 생성용 Serializer 클래스
class UserCreateSerializer(serializers.ModelSerializer[User]):
    # password 필드 정의 (쓰기 전용으로 설정)
    password = serializers.CharField(write_only=True)

    class Meta:
        # User 모델을 사용
        model = User
        fields = ["user_id", "password", "nickname", "email", "gender"]
        # 직렬화에서 처리할 필드 지정
        extra_kwargs = {
            "gender": {"required": False},
            # gender 필드를 필수 입력이 아닌 선택 입력으로 설정
        }

    # 사용자 생성을 처리하는 메서드
    def create(self, validated_data: Dict[str, Any]) -> User:
        # 입력 받은 비밀번호를 해싱하여 저장
        validated_data["password"] = make_password(validated_data.get("password"))
        # User 모델의 create 메서드를 호출하여 사용자 생성
        user: User = User.objects.create(**validated_data)
        # 생성된 사용자 객체 반환
        return user
