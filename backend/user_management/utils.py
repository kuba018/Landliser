from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token, password_reset_token

def send_verification_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    # Link do frontendu: /verify-email?uid=...&token=...
    backend_base = getattr(settings, "BACKEND_BASE_URL", "http://localhost:8000")
    activation_link = f"{backend_base}/api/user/verify-email/?uid={uid}&token={token}"

    subject = "Aktywacja konta Landliser"
    message = (
        f"Cześć {user.username or user.email},\n\n"
        f"Aby aktywować konto, kliknij w poniższy link:\n{activation_link}\n\n"
        "Jeśli to nie Ty zakładałeś konto, zignoruj tę wiadomość."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    
def send_password_reset_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token.make_token(user)

    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "http://localhost:5173")
    reset_link = f"{frontend_base}/reset-password?uid={uid}&token={token}"  

    subject = "Reset hasła w Landliser"
    message = (
        f"Cześć {user.username or user.email},\n\n"
        f"Aby ustawić nowe hasło, kliknij w poniższy link:\n{reset_link}\n\n"
        f"Jeśli to nie Ty inicjowałeś reset, zignoruj tę wiadomość."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )