import base64
from datetime import UTC, date, datetime

import pytest

from zgw_apis_client import CatalogiClient, DocumentenClient, ZakenClient
from zgw_apis_client.structs.documenten import EnkelvoudigInformatieObjectCreateData
from zgw_apis_client.structs.zaken import (
    MedewerkerIdentificatie,
    MedewerkerRol,
    MedewerkerRolCreateData,
    RolListParams,
    StatusCreateData,
    StatusListParams,
    Zaak,
    ZaakCreateData,
    ZaakInformatieObjectCreateData,
    ZaakInformatieObjectListParams,
    ZaakListParams,
)

from .data import RSIN, PublishedZaakType, create_published_zaaktype


@pytest.fixture
def published_zaaktype(catalogi_client: CatalogiClient) -> PublishedZaakType:
    return create_published_zaaktype(catalogi_client)


def _create_zaak(
    client: ZakenClient, setup: PublishedZaakType, *, omschrijving: str
) -> Zaak:
    return client.zaak.create(
        data=ZaakCreateData(
            zaaktype=setup.zaaktype.url,
            bronorganisatie=RSIN,
            verantwoordelijke_organisatie=RSIN,
            startdatum=date(2026, 2, 1),
            omschrijving=omschrijving,
        )
    )


@pytest.mark.vcr
def test_create_and_retrieve_zaak(
    zaken_client: ZakenClient, published_zaaktype: PublishedZaakType
):
    zaak = zaken_client.zaak.create(
        data=ZaakCreateData(
            zaaktype=published_zaaktype.zaaktype.url,
            bronorganisatie=RSIN,
            verantwoordelijke_organisatie=RSIN,
            startdatum=date(2026, 2, 1),
            omschrijving="Broken street light",
        )
    )

    assert zaak.identificatie
    assert zaak.zaaktype == published_zaaktype.zaaktype.url
    assert zaak.startdatum == date(2026, 2, 1)
    assert zaak.status is None
    assert zaak.einddatum is None

    by_url = zaken_client.zaak.retrieve(identifier=zaak.url)
    by_uuid = zaken_client.zaak.retrieve(identifier=zaak.uuid)
    assert by_url.omschrijving == by_uuid.omschrijving == "Broken street light"


@pytest.mark.vcr
def test_list_zaken(zaken_client: ZakenClient, published_zaaktype: PublishedZaakType):
    first = _create_zaak(zaken_client, published_zaaktype, omschrijving="First")
    second = _create_zaak(zaken_client, published_zaaktype, omschrijving="Second")

    page = zaken_client.zaak.list()
    assert page.count == 2
    assert {zaak.url for zaak in page.results} == {first.url, second.url}

    page = zaken_client.zaak.list(
        params=ZaakListParams(identificatie=second.identificatie)
    )
    assert [zaak.url for zaak in page.results] == [second.url]


@pytest.mark.vcr
def test_list_zaken_paginated(
    zaken_client: ZakenClient, published_zaaktype: PublishedZaakType
):
    for omschrijving in ("First", "Second", "Third"):
        _create_zaak(zaken_client, published_zaaktype, omschrijving=omschrijving)

    page = zaken_client.zaak.list(params=ZaakListParams(page_size=2))
    assert page.count == 3
    assert len(page.results) == 2
    assert page.next is not None

    page = zaken_client.zaak.list(params=ZaakListParams(page_size=2, page=2))
    assert len(page.results) == 1
    assert page.next is None


@pytest.mark.vcr
def test_statussen(zaken_client: ZakenClient, published_zaaktype: PublishedZaakType):
    received, in_progress, _closed = published_zaaktype.statustypen
    zaak = _create_zaak(zaken_client, published_zaaktype, omschrijving="Statuses")

    first = zaken_client.status.create(
        data=StatusCreateData(
            zaak=zaak.url,
            statustype=received.url,
            datum_status_gezet=datetime(2026, 2, 1, 9, 0, tzinfo=UTC),
            statustoelichting="Request received",
        )
    )
    second = zaken_client.status.create(
        data=StatusCreateData(
            zaak=zaak.url,
            statustype=in_progress.url,
            datum_status_gezet=datetime(2026, 2, 2, 9, 0, tzinfo=UTC),
        )
    )

    retrieved = zaken_client.status.retrieve(identifier=first.url)
    assert retrieved.statustoelichting == "Request received"
    assert retrieved.statustype == received.url
    assert retrieved.datum_status_gezet == datetime(2026, 2, 1, 9, 0, tzinfo=UTC)

    page = zaken_client.status.list(params=StatusListParams(zaak=zaak.url))
    assert page.count == 2

    page = zaken_client.status.list(
        params=StatusListParams(zaak=zaak.url, indicatie_laatst_gezette_status=True)
    )
    assert [status.url for status in page.results] == [second.url]

    assert zaken_client.zaak.retrieve(identifier=zaak.url).status == second.url


@pytest.mark.vcr
def test_medewerker_rollen(
    zaken_client: ZakenClient, published_zaaktype: PublishedZaakType
):
    zaak = _create_zaak(zaken_client, published_zaaktype, omschrijving="Roles")

    rol = zaken_client.rol.create(
        data=MedewerkerRolCreateData(
            zaak=zaak.url,
            roltype=published_zaaktype.roltype.url,
            roltoelichting="Assigned case handler",
            betrokkene_identificatie=MedewerkerIdentificatie(
                identificatie="employee-1",
                achternaam="Jansen",
                voorletters="J.",
            ),
        )
    )

    assert isinstance(rol, MedewerkerRol)
    assert rol.betrokkene_type == "medewerker"
    assert rol.omschrijving_generiek == "behandelaar"
    assert rol.betrokkene_identificatie is not None
    assert rol.betrokkene_identificatie.achternaam == "Jansen"

    retrieved = zaken_client.rol.retrieve(identifier=rol.url)
    assert retrieved == rol

    page = zaken_client.rol.list(params=RolListParams(zaak=zaak.url))
    assert page.results == [rol]

    page = zaken_client.rol.list(
        params=RolListParams(
            betrokkene_identificatie__medewerker__identificatie="employee-1"
        )
    )
    assert [r.url for r in page.results] == [rol.url]

    page = zaken_client.rol.list(
        params=RolListParams(
            betrokkene_identificatie__medewerker__identificatie="someone-else"
        )
    )
    assert page.count == 0

    page = zaken_client.zaak.list(
        params=ZaakListParams(
            rol__betrokkene_identificatie__medewerker__identificatie="employee-1"
        )
    )
    assert [c.url for c in page.results] == [zaak.url]


@pytest.mark.vcr
def test_zaakinformatieobjecten(
    zaken_client: ZakenClient,
    documenten_client: DocumentenClient,
    published_zaaktype: PublishedZaakType,
):
    zaak = _create_zaak(zaken_client, published_zaaktype, omschrijving="Documents")
    enkelvoudiginformatieobject = documenten_client.enkelvoudiginformatieobject.create(
        data=EnkelvoudigInformatieObjectCreateData(
            bronorganisatie=RSIN,
            creatiedatum=date(2026, 2, 1),
            titel="Photo of the street light",
            auteur="Applicant",
            taal="dut",
            informatieobjecttype=published_zaaktype.informatieobjecttype.url,
            bestandsnaam="photo.txt",
            inhoud=base64.b64encode(b"not really a photo").decode(),
        )
    )

    zaakinformatieobject = zaken_client.zaakinformatieobject.create(
        data=ZaakInformatieObjectCreateData(
            zaak=zaak.url, informatieobject=enkelvoudiginformatieobject.url
        )
    )
    assert zaakinformatieobject.zaak == zaak.url
    assert zaakinformatieobject.informatieobject == enkelvoudiginformatieobject.url

    zaakinformatieobjecten = zaken_client.zaakinformatieobject.list(
        params=ZaakInformatieObjectListParams(zaak=zaak.url)
    )
    assert zaakinformatieobjecten == [zaakinformatieobject]
