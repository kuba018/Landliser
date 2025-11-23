from dataclasses import dataclass
from decimal import Decimal
from typing import List
import requests


BASE_URL = "https://uldk.gugik.gov.pl/"


class ULDKError(Exception):
    pass


@dataclass
class ULDKParcelData:
    parcel_id: str          # identyfikator podany przez użytkownika
    voivodeship: str        # np. "podkarpackie"
    county: str             # np. "powiat lubaczowski"
    commune: str            # np. "Lubaczów (miasto)"
    region: str             # np. "Lubaczów Miasto"
    parcel_number: str      # np. "5558"

    srid: int               # np. 2180
    geom_wkt: str           # "POLYGON((...))"

    area_m2: Decimal        # wyliczona powierzchnia


def _call_uldk(params: dict) -> str:
    try:
        resp = requests.get(BASE_URL, params=params, timeout=5)
    except requests.RequestException as exc:
        raise ULDKError("Nie udało się połączyć z usługą ULDK.") from exc

    if resp.status_code != 200:
        raise ULDKError(f"ULDK zwróciło kod HTTP {resp.status_code}")

    text = resp.text.strip()
    if not text:
        raise ULDKError("ULDK zwróciło pustą odpowiedź.")

    return text


def _parse_polygon_wkt(wkt: str) -> List[tuple]:
    wkt = wkt.strip()
    if not wkt.upper().startswith("POLYGON"):
        raise ULDKError(f"Nieobsługiwany typ geometrii: {wkt[:20]}")

    inside = wkt[wkt.index("((") + 2 : wkt.rindex("))")]
    coords = []
    for pair in inside.split(","):
        x, y = pair.strip().split()
        coords.append((float(x), float(y)))

    return coords


def _shoelace(coords: List[tuple]) -> float:
    area = 0.0
    n = len(coords)
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def get_parcel_from_uldk(parcel_id: str) -> ULDKParcelData:
    """
    NOWA FINALNA FUNKCJA:
    - pobiera dane z ULDK,
    - zwraca ULDKParcelData z nazwami administracyjnymi + geometrią + powierzchnią.
    """

    params = {
        "request": "GetParcelByIdOrNr",
        "id": parcel_id,
        "result": "voivodeship,county,commune,region,parcel,geom_wkt",
        "srid": "2180",
    }

    raw = _call_uldk(params)
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]

    if len(lines) < 2:
        raise ULDKError("Niepoprawna odpowiedź ULDK.")

    if lines[0] == "0":
        raise ULDKError("Działka nie została odnaleziona.")

    fields = lines[1].split("|")
    if len(fields) != 6:
        raise ULDKError("Nieoczekiwana liczba pól w odpowiedzi ULDK.")

    voivodeship = fields[0]
    county = fields[1]
    commune = fields[2]
    region = fields[3]
    parcel_number = fields[4]

    geom_raw = fields[5]
    if geom_raw.startswith("SRID="):
        srid_str, wkt = geom_raw.split(";", 1)
        srid = int(srid_str.replace("SRID=", ""))
        geom_wkt = wkt.strip()
    else:
        srid = 2180
        geom_wkt = geom_raw

    # LICZENIE POWIERZCHNI
    coords = _parse_polygon_wkt(geom_wkt)
    area_m2 = Decimal(str(_shoelace(coords)))

    return ULDKParcelData(
        parcel_id=parcel_id,
        voivodeship=voivodeship,
        county=county,
        commune=commune,
        region=region,
        parcel_number=parcel_number,
        srid=srid,
        geom_wkt=geom_wkt,
        area_m2=area_m2,
    )
