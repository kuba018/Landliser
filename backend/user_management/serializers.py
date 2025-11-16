from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .tokens import password_reset_token
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'phone_number', 'is_verified', 'date_joined', 'last_login')
        read_only_fields = ('id', 'is_verified', 'date_joined', 'last_login')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password',)

    def validate(self, attrs):
        try:
            validate_password(attrs.get('password'))
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError("Both username/email and password are required.")

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username/email or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

        # tworzymy tokeny JWT (access + refresh)
        refresh = RefreshToken.for_user(user)

        # aktualizuj last_login, jeśli używasz tego pola
        update_last_login(None, user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        }

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        # Opcja 1: NIE wywalamy błędu, nawet jeśli mail nie istnieje (bez ujawniania użytkowników)
        # Opcja 2: jak chcesz, możesz sprawdzić, czy jest user – ale ja zrobię wersję bezpieczniejszą.
        self.user = User.objects.filter(email__iexact=value).first()
        return value

    def get_user(self):
        return getattr(self, "user", None)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        uid = attrs.get("uid")
        token = attrs.get("token")
        new_password = attrs.get("new_password")

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError({"uid": "Nieprawidłowy identyfikator użytkownika."})

        if not password_reset_token.check_token(user, token):
            raise serializers.ValidationError({"token": "Token jest nieprawidłowy lub wygasł."})

        # Walidacja hasła zgodnie z ustawieniami Django + Twoim customowym validatorem
        try:
            validate_password(new_password, user=user)
        except Exception as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})

        self.user = user
        return attrs

    def save(self, **kwargs):
        user = self.user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user