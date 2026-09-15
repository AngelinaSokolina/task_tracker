from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT с дополнительными полями: role, full_name."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['full_name'] = self.user.full_name
        return data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'phone', 'full_name', 'position', 'role', 'password']
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class RegisterEmployeeSerializer(serializers.ModelSerializer):
    """Регистрация сотрудника руководителем — возвращает сгенерированный пароль."""
    password = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'phone', 'full_name', 'position', 'password']
        read_only_fields = ['id', 'password']