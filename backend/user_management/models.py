from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # username już jest unique=True w AbstractUser
    email = models.EmailField(unique=True)  # wymagane do logowania po mailu
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username or self.email
