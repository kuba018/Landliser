from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import Parcel, Criterion
from .serializers import (
    ParcelListSerializer,
    ParcelDetailSerializer,
    CriterionSerializer,
    CriterionCreateSerializer,
)
from .services.parcel_importer import import_parcel_for_user
from .uldk_client import ULDKError

class IsOwner(permissions.BasePermission):
    """
    Użytkownik może operować tylko na swoich działkach i kryteriach.
    """

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Parcel):
            return obj.user == request.user
        if isinstance(obj, Criterion):
            return obj.parcel.user == request.user
        return False


class ParcelViewSet(viewsets.ModelViewSet):
    """
    CRUD na działkach + endpoint do pobierania danych z ULDK.
    """

    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Każdy użytkownik widzi tylko własne działki
        return Parcel.objects.filter(user=self.request.user).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return ParcelListSerializer
        return ParcelDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("Nie możesz usuwać cudzych działek.")
        instance.delete()


    @action(detail=False, methods=['post'], url_path='scrape')
    def scrape(self, request):
        """
        Pobiera dane działki z ULDK i zapisuje ją w bazie.

        Body:
        {
            "parcel_id": "180901_1.0001.5558"
        }
        """
        parcel_id = request.data.get('parcel_id')

        if not parcel_id:
            return Response(
                {"detail": "Pole 'parcel_id' jest wymagane."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            parcel, created = import_parcel_for_user(request.user, parcel_id)
        except ULDKError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY
            )

        serializer = ParcelDetailSerializer(parcel, context={"request": request})
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], url_path='calculate-tax')
    def calculate_tax(self, request, pk=None):
        """
        POST /api/parcels/{id}/calculate-tax/

        Liczy łączną kwotę podatku na podstawie wszystkich kryteriów
        przypisanych do tej działki i zapisuje wynik w Parcel.total_tax_amount.
        """
        parcel = self.get_object()  # filtruje już po userze

        criteria = parcel.criteria.all()
        total = Decimal("0.00")

        for c in criteria:
            amount = c.tax_amount
            if amount is None and c.area_m2 is not None and c.rate_per_m2 is not None:
                amount = (c.area_m2 * c.rate_per_m2).quantize(Decimal("0.01"))
            if amount is not None:
                total += amount

        parcel.total_tax_amount = total
        parcel.save(update_fields=['total_tax_amount'])

        serializer = ParcelDetailSerializer(parcel, context={'request': request})
        return Response(
            {
                "parcel": serializer.data,
                "total_tax_amount": str(total),
                "criteria_count": criteria.count(),
            },
            status=status.HTTP_200_OK,
        )


class CriterionViewSet(viewsets.ModelViewSet):
    """
    CRUD dla kryteriów podatkowych.
    """

    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Criterion.objects.filter(parcel__user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CriterionCreateSerializer
        return CriterionSerializer

    def perform_create(self, serializer):
        parcel = serializer.validated_data.get('parcel')

        if parcel.user != self.request.user:
            raise PermissionDenied("Nie możesz dodawać kryteriów do cudzej działki.")

        serializer.save()
