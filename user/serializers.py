from typing import Any, Dict

from django.contrib.auth import authenticate  # 유저 인증을 처리하는 함수
from django.contrib.auth.hashers import make_password
from rest_framework import serializers  # DRF에서 제공하는 직렬화(Serializer) 도구
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User  # 사용자 정의 모델 임포트


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
        # 요청 데이터에서 username 추출
        username = attrs.get("username")
        # 요청 데이터에서 password 추출
        password = attrs.get("password")

        # username password가 모두 제공되었는지 확인
        if username and password:
            # Django의 authenticate 함수를 사용해 사용자 인증
            user = authenticate(
                username=username, password=password
            )  # username username으로 변경하여 사용

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
            attrs["username"] = username
            # 부모 클래스의 검증 로직 실행 및 결과 반환
            return super().validate(attrs)
        else:
            # username password가 누락된 경우 예외 발생
            raise serializers.ValidationError('Must include "username" and "password".')


# 사용자 생성용 Serializer 클래스
class UserCreateSerializer(serializers.ModelSerializer[User]):
    # password 필드는 입력 시에만 사용되고 반환 시에는 제외되는 필드입니다.
    password = serializers.CharField(write_only=True)

    class Meta:
        # 직렬화할 모델을 User 로 지정
        model = User
        # 직렬화할 필드들 지정
        fields = ["username", "password", "nickname", "email", "gender"]
        # gender 필드는 선택 사항이므로 extra_kwargs로 필수 여부를 False로 설정
        extra_kwargs = {
            "gender": {"required": False},
        }

    # 사용자가 제출한 데이터를 기반으로 사용자 객체를 생성하는 메서드
    def create(self, validated_data: Dict[str, Any]) -> User:
        # vlidataed_data에 포함된 데이터를 사용하여 User 객체 생성 (비밀번호는 해시화(암호화)) 하여 저장됨)
        user = User.objects.create_user(**validated_data)
        # 생성된 User 객체 반환
        return user
