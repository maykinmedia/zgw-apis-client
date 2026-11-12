"""
Helpers that set up the catalogue data cases and documents need.

The dates are fixed so the recorded cassettes keep matching.
"""

from dataclasses import dataclass
from datetime import date

from zgw_apis_client import CatalogiClient
from zgw_apis_client.structs.catalogi import (
    BrondatumArchiefprocedure,
    CaseType,
    CaseTypeCreateData,
    CaseTypeDocumentTypeCreateData,
    Catalogue,
    CatalogueCreateData,
    DocumentType,
    DocumentTypeCreateData,
    ReferentieProces,
    ResultType,
    ResultTypeCreateData,
    RoleType,
    RoleTypeCreateData,
    StatusType,
    StatusTypeCreateData,
)

RSIN = "517439943"
VALID_FROM = date(2026, 1, 1)

SELECTIELIJST = "https://selectielijst.openzaak.nl/api/v1"
SELECTIELIJST_PROCESTYPE = (
    f"{SELECTIELIJST}/procestypen/e1b73b12-b2f6-4c4e-8929-94f84dd2a57d"
)
SELECTIELIJST_RESULTAAT = (
    f"{SELECTIELIJST}/resultaten/cc5ae4e3-a9e6-4386-bcee-46be4986a829"
)
RESULTAATTYPEOMSCHRIJVING_AFGEHANDELD = (
    f"{SELECTIELIJST}/resultaattypeomschrijvingen/7cb315fb-4f7b-4a43-aca1-e4522e4c73b3"
)


def create_catalogue(client: CatalogiClient) -> Catalogue:
    return client.catalogue.create(
        CatalogueCreateData(
            domein="TEST",
            rsin=RSIN,
            contactpersoon_beheer_naam="Test",
            naam="Test catalogue",
        )
    )


def create_document_type(
    client: CatalogiClient,
    catalogue: Catalogue,
    *,
    omschrijving: str = "Attachment",
    publish: bool = True,
) -> DocumentType:
    document_type = client.document_type.create(
        DocumentTypeCreateData(
            catalogus=catalogue.url,
            omschrijving=omschrijving,
            vertrouwelijkheidaanduiding="openbaar",
            begin_geldigheid=VALID_FROM,
            informatieobjectcategorie="Attachment",
        )
    )
    if publish:
        document_type = client.document_type.publish(document_type.url)
    return document_type


def create_concept_case_type(
    client: CatalogiClient,
    catalogue: Catalogue,
    *,
    identificatie: str = "TEST-CASE-TYPE",
    omschrijving: str = "Test case type",
) -> CaseType:
    return client.case_type.create(
        CaseTypeCreateData(
            catalogus=catalogue.url,
            identificatie=identificatie,
            omschrijving=omschrijving,
            vertrouwelijkheidaanduiding="openbaar",
            doel="Testing",
            aanleiding="Testing",
            indicatie_intern_of_extern="extern",
            handeling_initiator="Aanvragen",
            onderwerp="Test",
            handeling_behandelaar="Behandelen",
            doorlooptijd="P30D",
            opschorting_en_aanhouding_mogelijk=False,
            verlenging_mogelijk=False,
            publicatie_indicatie=False,
            referentieproces=ReferentieProces(naam="Test"),
            verantwoordelijke="Test",
            begin_geldigheid=VALID_FROM,
            versiedatum=VALID_FROM,
            selectielijst_procestype=SELECTIELIJST_PROCESTYPE,
        )
    )


@dataclass
class PublishedCaseType:
    case_type: CaseType
    status_types: tuple[StatusType, StatusType, StatusType]
    result_type: ResultType
    role_type: RoleType
    document_type: DocumentType


def create_published_case_type(
    client: CatalogiClient, catalogue: Catalogue | None = None
) -> PublishedCaseType:
    """
    A published case type with everything Open Zaak wants before publishing.
    """
    if catalogue is None:
        catalogue = create_catalogue(client)
    document_type = create_document_type(client, catalogue)
    case_type = create_concept_case_type(client, catalogue)

    client.case_type_document_type.create(
        CaseTypeDocumentTypeCreateData(
            zaaktype=case_type.url,
            informatieobjecttype=document_type.url,
            volgnummer=1,
            richting="inkomend",
        )
    )
    status_types = (
        client.status_type.create(
            StatusTypeCreateData(
                zaaktype=case_type.url, omschrijving="Received", volgnummer=1
            )
        ),
        client.status_type.create(
            StatusTypeCreateData(
                zaaktype=case_type.url, omschrijving="In progress", volgnummer=2
            )
        ),
        # final status: Open Zaak only accepts it once the case has a result
        client.status_type.create(
            StatusTypeCreateData(
                zaaktype=case_type.url, omschrijving="Closed", volgnummer=3
            )
        ),
    )
    result_type = client.result_type.create(
        ResultTypeCreateData(
            zaaktype=case_type.url,
            omschrijving="Handled",
            resultaattypeomschrijving=RESULTAATTYPEOMSCHRIJVING_AFGEHANDELD,
            selectielijstklasse=SELECTIELIJST_RESULTAAT,
            archiefnominatie="vernietigen",
            archiefactietermijn="P10Y",
            brondatum_archiefprocedure=BrondatumArchiefprocedure(
                afleidingswijze="afgehandeld"
            ),
        )
    )
    role_type = client.role_type.create(
        RoleTypeCreateData(
            zaaktype=case_type.url,
            omschrijving="Case handler",
            omschrijving_generiek="behandelaar",
        )
    )
    case_type = client.case_type.publish(case_type.url)

    return PublishedCaseType(
        case_type=case_type,
        status_types=status_types,
        result_type=result_type,
        role_type=role_type,
        document_type=document_type,
    )
