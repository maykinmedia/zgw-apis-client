"""
Helpers that set up the catalogue data cases and documents need.

The dates are fixed so the recorded cassettes keep matching.
"""

from dataclasses import dataclass
from datetime import date

from zgw_apis_client import CatalogiClient
from zgw_apis_client.structs.catalogi import (
    BrondatumArchiefprocedure,
    Catalogus,
    CatalogusCreateData,
    InformatieObjectType,
    InformatieObjectTypeCreateData,
    ReferentieProces,
    ResultaatType,
    ResultaatTypeCreateData,
    RolType,
    RolTypeCreateData,
    StatusType,
    StatusTypeCreateData,
    ZaakType,
    ZaakTypeCreateData,
    ZaakTypeInformatieObjectTypeCreateData,
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


def create_catalogus(client: CatalogiClient) -> Catalogus:
    return client.catalogus.create(
        data=CatalogusCreateData(
            domein="TEST",
            rsin=RSIN,
            contactpersoon_beheer_naam="Test",
            naam="Test catalogue",
        )
    )


def create_informatieobjecttype(
    client: CatalogiClient,
    catalogus: Catalogus,
    *,
    omschrijving: str = "Attachment",
    publish: bool = True,
) -> InformatieObjectType:
    informatieobjecttype = client.informatieobjecttype.create(
        data=InformatieObjectTypeCreateData(
            catalogus=catalogus.url,
            omschrijving=omschrijving,
            vertrouwelijkheidaanduiding="openbaar",
            begin_geldigheid=VALID_FROM,
            informatieobjectcategorie="Attachment",
        )
    )
    if publish:
        informatieobjecttype = client.informatieobjecttype.publish(
            identifier=informatieobjecttype.url
        )
    return informatieobjecttype


def create_concept_zaaktype(
    client: CatalogiClient,
    catalogus: Catalogus,
    *,
    identificatie: str = "TEST-CASE-TYPE",
    omschrijving: str = "Test case type",
) -> ZaakType:
    return client.zaaktype.create(
        data=ZaakTypeCreateData(
            catalogus=catalogus.url,
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
class PublishedZaakType:
    zaaktype: ZaakType
    statustypen: tuple[StatusType, StatusType, StatusType]
    resultaattype: ResultaatType
    roltype: RolType
    informatieobjecttype: InformatieObjectType


def create_published_zaaktype(
    client: CatalogiClient, catalogus: Catalogus | None = None
) -> PublishedZaakType:
    """
    A published case type with everything Open Zaak wants before publishing.
    """
    if catalogus is None:
        catalogus = create_catalogus(client)
    informatieobjecttype = create_informatieobjecttype(client, catalogus)
    zaaktype = create_concept_zaaktype(client, catalogus)

    client.zaaktype_informatieobjecttype.create(
        data=ZaakTypeInformatieObjectTypeCreateData(
            zaaktype=zaaktype.url,
            informatieobjecttype=informatieobjecttype.url,
            volgnummer=1,
            richting="inkomend",
        )
    )
    statustypen = (
        client.statustype.create(
            data=StatusTypeCreateData(
                zaaktype=zaaktype.url, omschrijving="Received", volgnummer=1
            )
        ),
        client.statustype.create(
            data=StatusTypeCreateData(
                zaaktype=zaaktype.url, omschrijving="In progress", volgnummer=2
            )
        ),
        # final status: Open Zaak only accepts it once the case has a result
        client.statustype.create(
            data=StatusTypeCreateData(
                zaaktype=zaaktype.url, omschrijving="Closed", volgnummer=3
            )
        ),
    )
    resultaattype = client.resultaattype.create(
        data=ResultaatTypeCreateData(
            zaaktype=zaaktype.url,
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
    roltype = client.roltype.create(
        data=RolTypeCreateData(
            zaaktype=zaaktype.url,
            omschrijving="Case handler",
            omschrijving_generiek="behandelaar",
        )
    )
    zaaktype = client.zaaktype.publish(identifier=zaaktype.url)

    return PublishedZaakType(
        zaaktype=zaaktype,
        statustypen=statustypen,
        resultaattype=resultaattype,
        roltype=roltype,
        informatieobjecttype=informatieobjecttype,
    )
