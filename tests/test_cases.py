import base64
from datetime import UTC, date, datetime

import pytest

from tests.data import RSIN, PublishedCaseType, create_published_case_type
from zgw_apis_client import CasesClient, CatalogiClient, DocumentsClient
from zgw_apis_client.structs.cases import (
    Case,
    CaseCreateData,
    CaseDocumentCreateData,
    CaseDocumentListParams,
    CaseListParams,
    EmployeeRole,
    EmployeeRoleCreateData,
    MedewerkerIdentificatie,
    RoleListParams,
    StatusCreateData,
    StatusListParams,
)
from zgw_apis_client.structs.documents import DocumentCreateData


@pytest.fixture
def published_case_type(catalogi_client: CatalogiClient) -> PublishedCaseType:
    return create_published_case_type(catalogi_client)


def _create_case(
    client: CasesClient, setup: PublishedCaseType, *, omschrijving: str
) -> Case:
    return client.case.create(
        CaseCreateData(
            zaaktype=setup.case_type.url,
            bronorganisatie=RSIN,
            verantwoordelijke_organisatie=RSIN,
            startdatum=date(2026, 2, 1),
            omschrijving=omschrijving,
        )
    )


@pytest.mark.vcr
def test_create_and_retrieve_case(
    cases_client: CasesClient, published_case_type: PublishedCaseType
):
    case = cases_client.case.create(
        CaseCreateData(
            zaaktype=published_case_type.case_type.url,
            bronorganisatie=RSIN,
            verantwoordelijke_organisatie=RSIN,
            startdatum=date(2026, 2, 1),
            omschrijving="Broken street light",
        )
    )

    assert case.identificatie
    assert case.zaaktype == published_case_type.case_type.url
    assert case.startdatum == date(2026, 2, 1)
    assert case.status is None
    assert case.einddatum is None

    by_url = cases_client.case.retrieve(case.url)
    by_uuid = cases_client.case.retrieve(case.uuid)
    assert by_url.omschrijving == by_uuid.omschrijving == "Broken street light"


@pytest.mark.vcr
def test_list_cases(cases_client: CasesClient, published_case_type: PublishedCaseType):
    first = _create_case(cases_client, published_case_type, omschrijving="First")
    second = _create_case(cases_client, published_case_type, omschrijving="Second")

    page = cases_client.case.list()
    assert page.count == 2
    assert {case.url for case in page.results} == {first.url, second.url}

    page = cases_client.case.list(
        params=CaseListParams(identificatie=second.identificatie)
    )
    assert [case.url for case in page.results] == [second.url]


@pytest.mark.vcr
def test_list_cases_paginated(
    cases_client: CasesClient, published_case_type: PublishedCaseType
):
    for omschrijving in ("First", "Second", "Third"):
        _create_case(cases_client, published_case_type, omschrijving=omschrijving)

    page = cases_client.case.list(params=CaseListParams(page_size=2))
    assert page.count == 3
    assert len(page.results) == 2
    assert page.next is not None

    page = cases_client.case.list(params=CaseListParams(page_size=2, page=2))
    assert len(page.results) == 1
    assert page.next is None


@pytest.mark.vcr
def test_statuses(cases_client: CasesClient, published_case_type: PublishedCaseType):
    received, in_progress, _closed = published_case_type.status_types
    case = _create_case(cases_client, published_case_type, omschrijving="Statuses")

    first = cases_client.status.create(
        StatusCreateData(
            zaak=case.url,
            statustype=received.url,
            datum_status_gezet=datetime(2026, 2, 1, 9, 0, tzinfo=UTC),
            statustoelichting="Request received",
        )
    )
    second = cases_client.status.create(
        StatusCreateData(
            zaak=case.url,
            statustype=in_progress.url,
            datum_status_gezet=datetime(2026, 2, 2, 9, 0, tzinfo=UTC),
        )
    )

    retrieved = cases_client.status.retrieve(first.url)
    assert retrieved.statustoelichting == "Request received"
    assert retrieved.statustype == received.url
    assert retrieved.datum_status_gezet == datetime(2026, 2, 1, 9, 0, tzinfo=UTC)

    page = cases_client.status.list(params=StatusListParams(zaak=case.url))
    assert page.count == 2

    page = cases_client.status.list(
        params=StatusListParams(zaak=case.url, indicatie_laatst_gezette_status=True)
    )
    assert [status.url for status in page.results] == [second.url]

    assert cases_client.case.retrieve(case.url).status == second.url


@pytest.mark.vcr
def test_employee_roles(
    cases_client: CasesClient, published_case_type: PublishedCaseType
):
    case = _create_case(cases_client, published_case_type, omschrijving="Roles")

    role = cases_client.role.create(
        EmployeeRoleCreateData(
            zaak=case.url,
            roltype=published_case_type.role_type.url,
            roltoelichting="Assigned case handler",
            betrokkene_identificatie=MedewerkerIdentificatie(
                identificatie="employee-1",
                achternaam="Jansen",
                voorletters="J.",
            ),
        )
    )

    assert isinstance(role, EmployeeRole)
    assert role.betrokkene_type == "medewerker"
    assert role.omschrijving_generiek == "behandelaar"
    assert role.betrokkene_identificatie is not None
    assert role.betrokkene_identificatie.achternaam == "Jansen"

    retrieved = cases_client.role.retrieve(role.url)
    assert retrieved == role

    page = cases_client.role.list(params=RoleListParams(zaak=case.url))
    assert page.results == [role]

    page = cases_client.role.list(
        params=RoleListParams(
            betrokkene_identificatie__medewerker__identificatie="employee-1"
        )
    )
    assert [r.url for r in page.results] == [role.url]

    page = cases_client.role.list(
        params=RoleListParams(
            betrokkene_identificatie__medewerker__identificatie="someone-else"
        )
    )
    assert page.count == 0

    page = cases_client.case.list(
        params=CaseListParams(
            rol__betrokkene_identificatie__medewerker__identificatie="employee-1"
        )
    )
    assert [c.url for c in page.results] == [case.url]


@pytest.mark.vcr
def test_case_documents(
    cases_client: CasesClient,
    documents_client: DocumentsClient,
    published_case_type: PublishedCaseType,
):
    case = _create_case(cases_client, published_case_type, omschrijving="Documents")
    document = documents_client.document.create(
        DocumentCreateData(
            bronorganisatie=RSIN,
            creatiedatum=date(2026, 2, 1),
            titel="Photo of the street light",
            auteur="Applicant",
            taal="dut",
            informatieobjecttype=published_case_type.document_type.url,
            bestandsnaam="photo.txt",
            inhoud=base64.b64encode(b"not really a photo").decode(),
        )
    )

    case_document = cases_client.case_document.create(
        CaseDocumentCreateData(zaak=case.url, informatieobject=document.url)
    )
    assert case_document.zaak == case.url
    assert case_document.informatieobject == document.url

    case_documents = cases_client.case_document.list(
        params=CaseDocumentListParams(zaak=case.url)
    )
    assert case_documents == [case_document]
