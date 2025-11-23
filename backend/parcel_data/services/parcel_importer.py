from django.db import transaction
from ..models import Parcel
from ..uldk_client import get_parcel_from_uldk, ULDKError


@transaction.atomic
def import_parcel_for_user(user, parcel_id: str):
    """
    - pobiera dane działki z ULDK,
    - zapisuje lub aktualizuje rekord w bazie,
    - zwraca (parcel, created).
    """

    data = get_parcel_from_uldk(parcel_id)

    defaults = {
        "parcel_number": data.parcel_number,
        "voivodeship": data.voivodeship,
        "county": data.county,
        "commune": data.commune,
        "region": data.region,
        "area_m2": data.area_m2,
        "geom_wkt": data.geom_wkt,
        "total_tax_amount": None,
    }

    parcel, created = Parcel.objects.update_or_create(
        user=user,
        parcel_id=data.parcel_id,
        defaults=defaults,
    )

    return parcel, created
