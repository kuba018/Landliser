from django.conf import settings
from django.db import models
from decimal import Decimal 

class Parcel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="parcels"
    )

    # pełny identyfikator działki – dla starych rekordów może być pusty
    parcel_id = models.CharField(max_length=32, null=True, blank=True)

    # numer działki w obrębie – to już miałeś wcześniej, więc może zostać nie-null
    parcel_number = models.CharField(max_length=16)

    # nazwy jednostek administracyjnych – dla starych rekordów nie do odtworzenia
    voivodeship = models.CharField(max_length=64, null=True, blank=True)
    county = models.CharField(max_length=64, null=True, blank=True)
    commune = models.CharField(max_length=128, null=True, blank=True)
    region = models.CharField(max_length=128, null=True, blank=True)

    # nowe pola – też nie istnieją dla historycznych rekordów
    area_m2 = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        null=True,
        blank=True,
    )
    geom_wkt = models.TextField(null=True, blank=True)

    total_tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'parcel_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.parcel_id or self.parcel_number} ({self.user})"



class Criterion(models.Model):
    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name='criteria',
    )

    # opis słowny, wielozdaniowy
    description = models.TextField(
        null=True,
        blank=True,
    )

    # powierzchnia w m², wymagana
    area_m2 = models.DecimalField(
        max_digits=16,
        decimal_places=2,
    )

    # stawka podatku w zł/m²
    rate_per_m2 = models.DecimalField(
        max_digits=10,
        decimal_places=4,
    )

    # kwota podatku = area * rate → liczona automatycznie
    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Kryterium #{self.pk} dla działki {self.parcel.parcel_number}'

    def recalc_tax(self):
        if self.area_m2 and self.rate_per_m2:
            self.tax_amount = (self.area_m2 * self.rate_per_m2).quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        self.recalc_tax()
        super().save(*args, **kwargs)
