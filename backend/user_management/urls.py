from django.urls import path

from .views import (
    RegisterView,
    MeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    VerifyEmailView,
    DeleteAccountView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('me/', MeView.as_view(), name='user-me'),
    path('verify-email/', VerifyEmailView.as_view(), name='user-verify-email'),
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
]
