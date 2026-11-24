from datetime import UTC, date, datetime
from unittest.mock import patch
from uuid import UUID

import msgspec
import pytest

from zgw_apis_client import ZakenClient
from zgw_apis_client.structs.base import PaginatedResponseBody
from zgw_apis_client.structs.catalogi import ZaakTypeListParams
from zgw_apis_client.structs.zaken import (
    NatuurlijkPersoonRol,
    Rol,
    StatusCreateData,
    Zaak,
    ZaakListParams,
)

ROL = {
    "url": "http://example.com/zaken/api/v1/rollen/1",
    "uuid": "a4ef6bc4-1ea1-4a2d-8f8f-a6d4b2d5c1b9",
    "zaak": "http://example.com/zaken/api/v1/zaken/1",
    "betrokkene": "",
    "roltype": "http://example.com/catalogi/api/v1/roltypen/1",
    "omschrijving": "Applicant",
    "omschrijvingGeneriek": "initiator",
    "roltoelichting": "",
    "registratiedatum": "2026-02-01T09:00:00Z",
    "indicatieMachtiging": "",
    "contactpersoonRol": None,
    "statussen": [],
    "beginGeldigheid": None,
    "eindeGeldigheid": None,
}


@pytest.fixture
def zaak() -> Zaak:
    return Zaak(
        url="http://example.com/zaken/api/v1/zaken/1",
        uuid=UUID("d6a1c2e0-3b4f-4c5d-9e8f-0a1b2c3d4e5f"),
        bronorganisatie="517439943",
        zaaktype="http://example.com/catalogi/api/v1/zaaktypen/1",
        verantwoordelijke_organisatie="517439943",
        startdatum=date(2026, 2, 1),
        einddatum=None,
        laatst_gemuteerd=datetime(2026, 2, 1, 9, 0, tzinfo=UTC),
        betalingsindicatie_weergave="",
        deelzaken=[],
        eigenschappen=[],
        rollen=[],
        status=None,
        zaakinformatieobjecten=[],
        zaakobjecten=[],
        resultaat=None,
    )


@pytest.mark.parametrize(
    ("einddatum", "expected"),
    [(None, False), (date(2026, 2, 10), True)],
    ids=["open", "closed"],
)
def test_zaak_is_closed_when_it_has_an_end_date(
    zaak: Zaak, einddatum: date | None, expected: bool
):
    zaak.einddatum = einddatum

    assert zaak.is_closed is expected


def test_query_params_keep_double_underscore_lookups():
    params = ZaakListParams(
        page_size=10,
        rol__betrokkene_identificatie__medewerker__identificatie="employee-1",
        einddatum__isnull=True,
    )

    assert params.as_params() == {
        "pageSize": 10,
        "einddatum__isnull": True,
        "rol__betrokkeneIdentificatie__medewerker__identificatie": "employee-1",
    }


def test_unset_query_params_are_left_out():
    assert ZaakTypeListParams().as_params() == {}


def test_rollen_other_than_medewerkers_are_accepted():
    """
    Another system may have added the applicant to the case. Listing roles shouldn't
    break on that.
    """
    data = {
        **ROL,
        "betrokkeneType": "natuurlijk_persoon",
        "betrokkeneIdentificatie": {"inpBsn": "111222333"},
    }

    page = msgspec.convert(
        {"count": 1, "next": None, "previous": None, "results": [data]},
        type=PaginatedResponseBody[Rol],
    )

    rol = page.results[0]
    assert isinstance(rol, NatuurlijkPersoonRol)
    assert rol.betrokkene_type == "natuurlijk_persoon"
    assert rol.betrokkene_identificatie == {"inpBsn": "111222333"}


def test_detail_path_from_uuid_or_url():
    client = ZakenClient("http://example.com/zaken/api/v1/")

    assert client.zaak._detail_path("1234") == "zaken/1234"
    assert (
        client.zaak._detail_path("http://example.com/zaken/api/v1/zaken/1234")
        == "http://example.com/zaken/api/v1/zaken/1234"
    )


def test_resource_must_be_bound_to_a_client():
    with pytest.raises(RuntimeError):
        ZakenClient.zaak.http_client  # noqa: B018


@pytest.mark.parametrize(
    "gezetdoor",
    ["http://example.com/zaken/api/v1/rollen/1", "https://example.com/rollen/1", None],
)
def test_url_fields_accept_urls_and_none(gezetdoor):
    data = {
        "zaak": "http://example.com/zaken/api/v1/zaken/1",
        "statustype": "http://example.com/catalogi/api/v1/statustypen/1",
        "datumStatusGezet": "2026-02-01T09:00:00Z",
        "gezetdoor": gezetdoor,
    }

    status = msgspec.convert(data, StatusCreateData)

    assert status.gezetdoor == gezetdoor


@pytest.mark.parametrize("value", ["", "1234", "example.com/zaken/1", "ftp://x"])
def test_url_fields_reject_non_urls(value):
    data = {
        "zaak": value,
        "statustype": "http://example.com/catalogi/api/v1/statustypen/1",
        "datumStatusGezet": "2026-02-01T09:00:00Z",
    }

    with pytest.raises(msgspec.ValidationError, match=r"\$\.zaak"):
        msgspec.convert(data, StatusCreateData)


def test_create_validates_payload_before_sending():
    client = ZakenClient("http://example.com/zaken/api/v1/")
    # the constructor doesn't validate, so this only fails in ``create``
    data = StatusCreateData(
        zaak="http://example.com/zaken/api/v1/zaken/1",
        statustype="not-a-url",
        datum_status_gezet=datetime(2026, 2, 1, 9, tzinfo=UTC),
    )

    with (
        patch.object(ZakenClient, "request") as mock_request,
        pytest.raises(msgspec.ValidationError, match=r"\$\.statustype"),
    ):
        client.status.create(data=data)

    mock_request.assert_not_called()
