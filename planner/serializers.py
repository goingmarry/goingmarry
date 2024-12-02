from typing import Any, Dict  # Dict를 추가하여 타입 힌트에 사용

from rest_framework import serializers

import planner.models

from .models import Planner


class PlannerSerializer(serializers.ModelSerializer):  # type: ignore
    """
    Planner 모델을 위한 직렬화 클래스
    """

    class Meta:
        model = Planner  # 직렬화할 모델을 지정합니다.
        fields = [
            "id",
            "user",
            "ordering_num",
            "title",
            "is_delete",
            "created_at",
            "updated_at",
        ]  # 직렬화할 필드 목록

    def create(self, validated_data: Dict[str, Any]) -> Planner:
        """
        새 Planner 객체를 생성할 때 호출되는 메서드.
        validated_data를 사용하여 새 객체를 생성합니다.
        """
        return Planner.objects.create(
            **validated_data
        )  # 유효성 검사를 통과한 데이터로 새 Planner 생성

    def update(self, instance: Planner, validated_data: Dict[str, Any]) -> Planner:
        """
        기존 Planner 객체를 업데이트할 때 호출되는 메서드.
        instance는 수정할 기존 객체를 나타내며, validated_data를 사용하여 필드를 업데이트합니다.
        """
        instance.ordering_num = validated_data.get(
            "ordering_num", instance.ordering_num
        )  # ordering_num 업데이트
        instance.title = validated_data.get("title", instance.title)  # title 업데이트
        instance.is_delete = validated_data.get(
            "is_delete", instance.is_delete
        )  # is_delete 업데이트
        instance.save()  # 변경 사항 저장
        return instance  # 업데이트된 객체 반환
