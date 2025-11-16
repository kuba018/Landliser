from django.contrib.auth import get_user_model
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .utils import send_verification_email, send_password_reset_email
from .tokens import email_verification_token, password_reset_token
from django.shortcuts import redirect
from django.conf import settings

User = get_user_model()


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        send_verification_email(self.request, user)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def _verify(self, uid, token):
        if not uid or not token:
            return Response({"detail": "Brak danych w linku."}, status=400)

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except Exception:
            return Response({"detail": "Nieprawidłowy link."}, status=400)

        if user.is_verified:
            # Jeśli już zweryfikowany, też kierujemy na login
            frontend_base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")
            return redirect(f"{frontend_base}?verified=1")

        if not email_verification_token.check_token(user, token):
            return Response({"detail": "Token jest nieprawidłowy lub wygasł."}, status=400)

        user.is_verified = True
        user.save()

        # ✔ tu przekierowanie!
        frontend_base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")
        return redirect(f"{frontend_base}?verified=1")

    def get(self, request):
        return self._verify(
            request.query_params.get("uid"),
            request.query_params.get("token"),
        )

    def post(self, request):
        return self._verify(
            request.data.get("uid"),
            request.data.get("token"),
        )


class PasswordResetRequestView(APIView):
    """
    Przyjmuje email, jeśli użytkownik istnieje, wysyła mail z linkiem resetu.
    Zawsze zwraca 200 z tym samym komunikatem (bez ujawniania, czy adres istnieje).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.get_user()
        if user:
            send_password_reset_email(request, user)
        return Response(
            {"detail": "Jeśli podany adres istnieje w systemie, wysłaliśmy link resetujący hasło."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    Przyjmuje uid + token + new_password, zmienia hasło.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Hasło zostało zmienione."},
            status=status.HTTP_200_OK,
        )
