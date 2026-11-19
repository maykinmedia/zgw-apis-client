import pytest

from zgw_apis_client import CatalogiClient
from zgw_apis_client.structs.catalogi import (
    CatalogusCreateData,
    InformatieObjectTypeListParams,
    ResultaatTypeListParams,
    RolTypeListParams,
    StatusTypeListParams,
    ZaakTypeListParams,
)

from .data import (
    RSIN,
    VALID_FROM,
    create_catalogus,
    create_concept_zaaktype,
    create_informatieobjecttype,
    create_published_zaaktype,
)


@pytest.mark.vcr
def test_create_and_publish_zaaktype(catalogi_client: CatalogiClient):
    setup = create_published_zaaktype(catalogi_client)

    zaaktype = setup.zaaktype
    assert not zaaktype.concept
    assert zaaktype.identificatie == "TEST-CASE-TYPE"
    assert zaaktype.begin_geldigheid == VALID_FROM
    assert set(zaaktype.statustypen) == {st.url for st in setup.statustypen}
    assert zaaktype.resultaattypen == [setup.resultaattype.url]
    assert zaaktype.roltypen == [setup.roltype.url]
    assert zaaktype.informatieobjecttypen == [setup.informatieobjecttype.url]


@pytest.mark.vcr
def test_list_zaaktypen(catalogi_client: CatalogiClient):
    catalogus = create_catalogus(catalogi_client)
    concept = create_concept_zaaktype(
        catalogi_client, catalogus, identificatie="CONCEPT"
    )
    published = create_published_zaaktype(catalogi_client, catalogus).zaaktype

    # concepts are hidden by default
    page = catalogi_client.zaaktype.list()
    assert page.count == 1
    assert page.results[0].url == published.url

    page = catalogi_client.zaaktype.list(params=ZaakTypeListParams(status="concept"))
    assert [zaaktype.url for zaaktype in page.results] == [concept.url]


@pytest.mark.vcr
def test_list_zaaktypen_filtered_by_catalogus(catalogi_client: CatalogiClient):
    published = create_published_zaaktype(catalogi_client).zaaktype
    other_catalogus = catalogi_client.catalogus.create(
        data=CatalogusCreateData(
            domein="OTHER", rsin=RSIN, contactpersoon_beheer_naam="Other"
        )
    )

    page = catalogi_client.zaaktype.list(
        params=ZaakTypeListParams(catalogus=published.catalogus)
    )
    assert page.count == 1

    page = catalogi_client.zaaktype.list(
        params=ZaakTypeListParams(catalogus=other_catalogus.url)
    )
    assert page.count == 0


@pytest.mark.vcr
def test_retrieve_zaaktype_by_uuid_and_url(catalogi_client: CatalogiClient):
    zaaktype = create_published_zaaktype(catalogi_client).zaaktype
    uuid = zaaktype.url.rsplit("/", 1)[-1]

    by_url = catalogi_client.zaaktype.retrieve(identifier=zaaktype.url)
    by_uuid = catalogi_client.zaaktype.retrieve(identifier=uuid)

    assert by_url == by_uuid == zaaktype


@pytest.mark.vcr
def test_retrieve_and_list_informatieobjecttypen(catalogi_client: CatalogiClient):
    catalogus = create_catalogus(catalogi_client)
    published = create_informatieobjecttype(
        catalogi_client, catalogus, omschrijving="Letter"
    )
    concept = create_informatieobjecttype(
        catalogi_client, catalogus, omschrijving="Draft", publish=False
    )

    retrieved = catalogi_client.informatieobjecttype.retrieve(identifier=published.url)
    assert retrieved.omschrijving == "Letter"
    assert not retrieved.concept

    page = catalogi_client.informatieobjecttype.list()
    assert [informatieobjecttype.url for informatieobjecttype in page.results] == [
        published.url
    ]

    page = catalogi_client.informatieobjecttype.list(
        params=InformatieObjectTypeListParams(status="alles")
    )
    assert {informatieobjecttype.url for informatieobjecttype in page.results} == {
        published.url,
        concept.url,
    }


@pytest.mark.vcr
def test_retrieve_and_list_statustypen(catalogi_client: CatalogiClient):
    setup = create_published_zaaktype(catalogi_client)
    received, in_progress, closed = setup.statustypen

    retrieved = catalogi_client.statustype.retrieve(identifier=closed.url)
    assert retrieved.omschrijving == "Closed"
    assert retrieved.volgnummer == 3
    assert retrieved.is_eindstatus
    assert not catalogi_client.statustype.retrieve(
        identifier=received.url
    ).is_eindstatus
    assert retrieved.zaaktype == setup.zaaktype.url

    page = catalogi_client.statustype.list(
        params=StatusTypeListParams(zaaktype=setup.zaaktype.url)
    )
    assert page.count == 3
    assert {statustype.url for statustype in page.results} == {
        received.url,
        in_progress.url,
        closed.url,
    }


@pytest.mark.vcr
def test_retrieve_and_list_resultaattypen(catalogi_client: CatalogiClient):
    setup = create_published_zaaktype(catalogi_client)

    retrieved = catalogi_client.resultaattype.retrieve(
        identifier=setup.resultaattype.url
    )
    assert retrieved.omschrijving == "Handled"
    assert retrieved.archiefnominatie == "vernietigen"
    assert retrieved.brondatum_archiefprocedure is not None
    assert retrieved.brondatum_archiefprocedure.afleidingswijze == "afgehandeld"

    page = catalogi_client.resultaattype.list(
        params=ResultaatTypeListParams(zaaktype=setup.zaaktype.url)
    )
    assert [resultaattype.url for resultaattype in page.results] == [
        setup.resultaattype.url
    ]


@pytest.mark.vcr
def test_retrieve_and_list_roltypen(catalogi_client: CatalogiClient):
    setup = create_published_zaaktype(catalogi_client)

    retrieved = catalogi_client.roltype.retrieve(identifier=setup.roltype.url)
    assert retrieved.omschrijving == "Case handler"
    assert retrieved.omschrijving_generiek == "behandelaar"

    page = catalogi_client.roltype.list(
        params=RolTypeListParams(
            zaaktype=setup.zaaktype.url, omschrijving_generiek="behandelaar"
        )
    )
    assert [roltype.url for roltype in page.results] == [setup.roltype.url]

    page = catalogi_client.roltype.list(
        params=RolTypeListParams(omschrijving_generiek="initiator")
    )
    assert page.count == 0
