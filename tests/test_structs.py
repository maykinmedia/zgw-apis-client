import msgspec
import pytest

from zgw_apis_client import CasesClient
from zgw_apis_client.structs.base import PaginatedResponseBody
from zgw_apis_client.structs.cases import (
    CaseListParams,
    EmployeeRoleCreateData,
    MedewerkerIdentificatie,
    NaturalPersonRole,
    Role,
)
from zgw_apis_client.structs.catalogi import CaseTypeListParams

ROLE = {
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


def test_query_params_keep_double_underscore_lookups():
    params = CaseListParams(
        page_size=10,
        rol__betrokkene_identificatie__medewerker__identificatie="employee-1",
        einddatum__isnull=True,
    )

    assert msgspec.to_builtins(params) == {
        "pageSize": 10,
        "einddatum__isnull": True,
        "rol__betrokkeneIdentificatie__medewerker__identificatie": "employee-1",
    }


def test_unset_query_params_are_left_out():
    assert msgspec.to_builtins(CaseTypeListParams()) == {}


def test_employee_role_create_data_includes_betrokkene_type():
    data = EmployeeRoleCreateData(
        zaak="http://example.com/zaak",
        roltype="http://example.com/roltype",
        betrokkene_identificatie=MedewerkerIdentificatie(identificatie="employee-1"),
    )

    encoded = msgspec.to_builtins(data)

    assert encoded["betrokkeneType"] == "medewerker"
    assert encoded["betrokkeneIdentificatie"]["identificatie"] == "employee-1"


def test_roles_other_than_employees_are_accepted():
    """
    Another system may have added the applicant to the case. Listing roles shouldn't
    break on that.
    """
    data = {
        **ROLE,
        "betrokkeneType": "natuurlijk_persoon",
        "betrokkeneIdentificatie": {"inpBsn": "111222333"},
    }

    page = msgspec.convert(
        {"count": 1, "next": None, "previous": None, "results": [data]},
        type=PaginatedResponseBody[Role],
    )

    role = page.results[0]
    assert isinstance(role, NaturalPersonRole)
    assert role.betrokkene_type == "natuurlijk_persoon"
    assert role.betrokkene_identificatie == {"inpBsn": "111222333"}


def test_detail_path_from_uuid_or_url():
    client = CasesClient("http://example.com/zaken/api/v1/")

    assert client.case._detail_path("1234") == "zaken/1234"
    assert (
        client.case._detail_path("http://example.com/zaken/api/v1/zaken/1234")
        == "http://example.com/zaken/api/v1/zaken/1234"
    )


def test_resource_must_be_bound_to_a_client():
    with pytest.raises(RuntimeError):
        CasesClient.case.http_client  # noqa: B018
