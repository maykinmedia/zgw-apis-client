import pytest

from tests.data import (
    RSIN,
    VALID_FROM,
    create_catalogue,
    create_concept_case_type,
    create_document_type,
    create_published_case_type,
)
from zgw_apis_client import CatalogiClient
from zgw_apis_client.structs.catalogi import (
    CaseTypeListParams,
    CatalogueCreateData,
    DocumentTypeListParams,
    ResultTypeListParams,
    RoleTypeListParams,
    StatusTypeListParams,
)


@pytest.mark.vcr
def test_create_and_publish_case_type(catalogi_client: CatalogiClient):
    setup = create_published_case_type(catalogi_client)

    case_type = setup.case_type
    assert not case_type.concept
    assert case_type.identificatie == "TEST-CASE-TYPE"
    assert case_type.begin_geldigheid == VALID_FROM
    assert set(case_type.statustypen) == {st.url for st in setup.status_types}
    assert case_type.resultaattypen == [setup.result_type.url]
    assert case_type.roltypen == [setup.role_type.url]
    assert case_type.informatieobjecttypen == [setup.document_type.url]


@pytest.mark.vcr
def test_list_case_types(catalogi_client: CatalogiClient):
    catalogue = create_catalogue(catalogi_client)
    concept = create_concept_case_type(
        catalogi_client, catalogue, identificatie="CONCEPT"
    )
    published = create_published_case_type(catalogi_client, catalogue).case_type

    # concepts are hidden by default
    page = catalogi_client.case_type.list()
    assert page.count == 1
    assert page.results[0].url == published.url

    page = catalogi_client.case_type.list(params=CaseTypeListParams(status="concept"))
    assert [case_type.url for case_type in page.results] == [concept.url]


@pytest.mark.vcr
def test_list_case_types_filtered_by_catalogue(catalogi_client: CatalogiClient):
    published = create_published_case_type(catalogi_client).case_type
    other_catalogue = catalogi_client.catalogue.create(
        CatalogueCreateData(
            domein="OTHER", rsin=RSIN, contactpersoon_beheer_naam="Other"
        )
    )

    page = catalogi_client.case_type.list(
        params=CaseTypeListParams(catalogus=published.catalogus)
    )
    assert page.count == 1

    page = catalogi_client.case_type.list(
        params=CaseTypeListParams(catalogus=other_catalogue.url)
    )
    assert page.count == 0


@pytest.mark.vcr
def test_retrieve_case_type_by_uuid_and_url(catalogi_client: CatalogiClient):
    case_type = create_published_case_type(catalogi_client).case_type
    uuid = case_type.url.rsplit("/", 1)[-1]

    by_url = catalogi_client.case_type.retrieve(case_type.url)
    by_uuid = catalogi_client.case_type.retrieve(uuid)

    assert by_url == by_uuid == case_type


@pytest.mark.vcr
def test_retrieve_and_list_document_types(catalogi_client: CatalogiClient):
    catalogue = create_catalogue(catalogi_client)
    published = create_document_type(catalogi_client, catalogue, omschrijving="Letter")
    concept = create_document_type(
        catalogi_client, catalogue, omschrijving="Draft", publish=False
    )

    retrieved = catalogi_client.document_type.retrieve(published.url)
    assert retrieved.omschrijving == "Letter"
    assert not retrieved.concept

    page = catalogi_client.document_type.list()
    assert [document_type.url for document_type in page.results] == [published.url]

    page = catalogi_client.document_type.list(
        params=DocumentTypeListParams(status="alles")
    )
    assert {document_type.url for document_type in page.results} == {
        published.url,
        concept.url,
    }


@pytest.mark.vcr
def test_retrieve_and_list_status_types(catalogi_client: CatalogiClient):
    setup = create_published_case_type(catalogi_client)
    received, in_progress, closed = setup.status_types

    retrieved = catalogi_client.status_type.retrieve(closed.url)
    assert retrieved.omschrijving == "Closed"
    assert retrieved.volgnummer == 3
    assert retrieved.is_eindstatus
    assert not catalogi_client.status_type.retrieve(received.url).is_eindstatus
    assert retrieved.zaaktype == setup.case_type.url

    page = catalogi_client.status_type.list(
        params=StatusTypeListParams(zaaktype=setup.case_type.url)
    )
    assert page.count == 3
    assert {status_type.url for status_type in page.results} == {
        received.url,
        in_progress.url,
        closed.url,
    }


@pytest.mark.vcr
def test_retrieve_and_list_result_types(catalogi_client: CatalogiClient):
    setup = create_published_case_type(catalogi_client)

    retrieved = catalogi_client.result_type.retrieve(setup.result_type.url)
    assert retrieved.omschrijving == "Handled"
    assert retrieved.archiefnominatie == "vernietigen"
    assert retrieved.brondatum_archiefprocedure is not None
    assert retrieved.brondatum_archiefprocedure.afleidingswijze == "afgehandeld"

    page = catalogi_client.result_type.list(
        params=ResultTypeListParams(zaaktype=setup.case_type.url)
    )
    assert [result_type.url for result_type in page.results] == [setup.result_type.url]


@pytest.mark.vcr
def test_retrieve_and_list_role_types(catalogi_client: CatalogiClient):
    setup = create_published_case_type(catalogi_client)

    retrieved = catalogi_client.role_type.retrieve(setup.role_type.url)
    assert retrieved.omschrijving == "Case handler"
    assert retrieved.omschrijving_generiek == "behandelaar"

    page = catalogi_client.role_type.list(
        params=RoleTypeListParams(
            zaaktype=setup.case_type.url, omschrijving_generiek="behandelaar"
        )
    )
    assert [role_type.url for role_type in page.results] == [setup.role_type.url]

    page = catalogi_client.role_type.list(
        params=RoleTypeListParams(omschrijving_generiek="initiator")
    )
    assert page.count == 0
