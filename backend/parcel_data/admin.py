from django.contrib import admin

from django.contrib import admin
from .models import Parcel, Criterion


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'parcel_id',
        'parcel_number',
        'voivodeship',
        'county',
        'commune',
        'region',
        'area_m2',
        'total_tax_amount',
        'created_at',
    )
    list_filter = ('voivodeship', 'county', 'commune')
    search_fields = ('parcel_id', 'parcel_number', 'user__username')
    ordering = ('-created_at',)


@admin.register(Criterion)
class CriterionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'parcel',
        # dorzucisz tu później pola z modelu Criterion
    )
    search_fields = ('parcel__parcel_id', 'parcel__parcel_number')

