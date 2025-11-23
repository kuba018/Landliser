from rest_framework import serializers
from .models import Parcel, Criterion

class CriterionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Criterion
        fields = [
            'parcel',
            'description',
            'area_m2',
            'rate_per_m2',
        ]

    def validate(self, attrs):
        description = attrs.get('description')
        if not description:
            raise serializers.ValidationError({
                "description": "Opis kryterium jest wymagany."
            })

        if attrs.get('area_m2') is not None and attrs['area_m2'] <= 0:
            raise serializers.ValidationError({
                "area_m2": "Powierzchnia musi być większa od zera."
            })

        if attrs.get('rate_per_m2') is not None and attrs['rate_per_m2'] < 0:
            raise serializers.ValidationError({
                "rate_per_m2": "Stawka nie może być ujemna."
            })

        return attrs

class CriterionSerializer(serializers.ModelSerializer):
    parcel_id = serializers.IntegerField(source='parcel.id', read_only=True)

    class Meta:
        model = Criterion
        fields = [
            'id',
            'parcel_id',
            'description',
            'area_m2',
            'rate_per_m2',
            'tax_amount',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'parcel_id',
            'tax_amount',
            'created_at',
            'updated_at',
        ]

class ParcelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = [
            'id',
            'parcel_id',
            'parcel_number',
            'area_m2',
            'voivodeship',
            'county',
            'commune',
            'region',
            'total_tax_amount',
            'created_at',
        ]
        read_only_fields = ['id', 'total_tax_amount', 'created_at', 'area_m2']


class ParcelDetailSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    criteria = CriterionSerializer(many=True, read_only=True)

    class Meta:
        model = Parcel
        fields = [
            'id',
            'user',
            'parcel_id',
            'parcel_number',
            'area_m2',
            'voivodeship',
            'county',
            'commune',
            'region',
            'geom_wkt',
            'total_tax_amount',
            'created_at',
            'criteria',
        ]
        read_only_fields = [
            'id',
            'area_m2',
            'geom_wkt',
            'total_tax_amount',
            'created_at',
        ]
