"""
Structs for the Catalogi API (1.3, as in Open Zaak 1.31).

Fields that aren't always in the response have a default.
"""

from collections.abc import Sequence
from datetime import date
from typing import Literal

import msgspec
from msgspec import UNSET, UnsetType

from .base import BaseSchemaStruct, PaginationParams
from .common import (
    Archiefnominatie,
    RolOmschrijvingGeneriek,
    Vertrouwelijkheidaanduiding,
)

type ConceptStatus = Literal["alles", "concept", "definitief"]
"""
Filter on the publication status. The API returns only published (``definitief``)
objects by default.
"""

type IndicatieInternOfExtern = Literal["intern", "extern"]

type Richting = Literal["inkomend", "intern", "uitgaand"]

type AardRelatie = Literal["vervolg", "bijdrage", "onderwerp"]

type Afleidingswijze = Literal[
    "afgehandeld",
    "ander_datumkenmerk",
    "eigenschap",
    "gerelateerde_zaak",
    "hoofdzaak",
    "ingangsdatum_besluit",
    "termijn",
    "vervaldatum_besluit",
    "zaakobject",
]


class ReferentieProces(BaseSchemaStruct):
    naam: str
    link: str = ""


class ZaakTypenRelatie(BaseSchemaStruct):
    zaaktype: str
    aard_relatie: AardRelatie
    toelichting: str = ""


class BronCatalogus(BaseSchemaStruct):
    url: str
    domein: str
    rsin: str


class BronZaaktype(BaseSchemaStruct):
    url: str
    identificatie: str
    omschrijving: str


class CheckListItem(BaseSchemaStruct):
    itemnaam: str
    vraagstelling: str
    toelichting: str = ""
    verplicht: bool = False


class InformatieObjectTypeOmschrijvingGeneriek(BaseSchemaStruct):
    informatieobjecttype_omschrijving_generiek: str
    definitie_informatieobjecttype_omschrijving_generiek: str
    herkomst_informatieobjecttype_omschrijving_generiek: str
    hierarchie_informatieobjecttype_omschrijving_generiek: str
    opmerking_informatieobjecttype_omschrijving_generiek: str = ""


class BrondatumArchiefprocedure(BaseSchemaStruct):
    afleidingswijze: Afleidingswijze
    datumkenmerk: str = ""
    einddatum_bekend: bool = False
    objecttype: str = ""
    registratie: str = ""
    procestermijn: str | None = None  # ISO 8601 duration


class CatalogueCreateData(BaseSchemaStruct):
    domein: str
    rsin: str
    contactpersoon_beheer_naam: str
    contactpersoon_beheer_telefoonnummer: str | UnsetType = UNSET
    contactpersoon_beheer_emailadres: str | UnsetType = UNSET
    naam: str | UnsetType = UNSET
    versie: str | UnsetType = UNSET
    begindatum_versie: date | None | UnsetType = UNSET


class Catalogue(BaseSchemaStruct):
    url: str
    domein: str
    rsin: str
    contactpersoon_beheer_naam: str
    contactpersoon_beheer_telefoonnummer: str = ""
    contactpersoon_beheer_emailadres: str = ""
    zaaktypen: Sequence[str]
    besluittypen: Sequence[str]
    informatieobjecttypen: Sequence[str]
    naam: str = ""
    versie: str = ""
    begindatum_versie: date | None = None


class CaseTypeListParams(PaginationParams):
    catalogus: str | UnsetType = UNSET
    datum_geldigheid: date | UnsetType = UNSET
    identificatie: str | UnsetType = UNSET
    status: ConceptStatus | UnsetType = UNSET
    trefwoorden: str | UnsetType = UNSET


class CaseTypeCreateData(BaseSchemaStruct):
    catalogus: str
    omschrijving: str
    vertrouwelijkheidaanduiding: Vertrouwelijkheidaanduiding
    doel: str
    aanleiding: str
    indicatie_intern_of_extern: IndicatieInternOfExtern
    handeling_initiator: str
    onderwerp: str
    handeling_behandelaar: str
    doorlooptijd: str  # ISO 8601 duration
    opschorting_en_aanhouding_mogelijk: bool
    verlenging_mogelijk: bool
    publicatie_indicatie: bool
    referentieproces: ReferentieProces
    verantwoordelijke: str
    begin_geldigheid: date
    versiedatum: date
    producten_of_diensten: Sequence[str] = msgspec.field(default_factory=list)
    besluittypen: Sequence[str] = msgspec.field(default_factory=list)
    gerelateerde_zaaktypen: Sequence[ZaakTypenRelatie] = msgspec.field(
        default_factory=list
    )
    identificatie: str | UnsetType = UNSET
    omschrijving_generiek: str | UnsetType = UNSET
    toelichting: str | UnsetType = UNSET
    servicenorm: str | None | UnsetType = UNSET
    verlengingstermijn: str | None | UnsetType = UNSET
    trefwoorden: Sequence[str] | UnsetType = UNSET
    publicatietekst: str | UnsetType = UNSET
    verantwoordingsrelatie: Sequence[str] | UnsetType = UNSET
    selectielijst_procestype: str | UnsetType = UNSET
    einde_geldigheid: date | None | UnsetType = UNSET
    deelzaaktypen: Sequence[str] | UnsetType = UNSET


class CaseType(BaseSchemaStruct):
    url: str
    identificatie: str = ""
    omschrijving: str
    omschrijving_generiek: str = ""
    vertrouwelijkheidaanduiding: Vertrouwelijkheidaanduiding
    doel: str
    aanleiding: str
    toelichting: str = ""
    indicatie_intern_of_extern: IndicatieInternOfExtern
    handeling_initiator: str
    onderwerp: str
    handeling_behandelaar: str
    doorlooptijd: str  # ISO 8601 duration
    servicenorm: str | None = None
    opschorting_en_aanhouding_mogelijk: bool
    verlenging_mogelijk: bool
    verlengingstermijn: str | None = None
    trefwoorden: Sequence[str] = ()
    publicatie_indicatie: bool
    publicatietekst: str = ""
    verantwoordingsrelatie: Sequence[str] = ()
    producten_of_diensten: Sequence[str]
    selectielijst_procestype: str = ""
    referentieproces: ReferentieProces
    concept: bool
    verantwoordelijke: str
    broncatalogus: BronCatalogus | None = None
    bronzaaktype: BronZaaktype | None = None
    begin_geldigheid: date
    einde_geldigheid: date | None = None
    versiedatum: date
    begin_object: date | None
    einde_object: date | None
    catalogus: str
    statustypen: Sequence[str]
    resultaattypen: Sequence[str]
    eigenschappen: Sequence[str]
    informatieobjecttypen: Sequence[str]
    roltypen: Sequence[str]
    besluittypen: Sequence[str]
    deelzaaktypen: Sequence[str] = ()
    gerelateerde_zaaktypen: Sequence[ZaakTypenRelatie]
    zaakobjecttypen: Sequence[str]


class DocumentTypeListParams(PaginationParams):
    catalogus: str | UnsetType = UNSET
    datum_geldigheid: date | UnsetType = UNSET
    omschrijving: str | UnsetType = UNSET
    status: ConceptStatus | UnsetType = UNSET
    zaaktype: str | UnsetType = UNSET


class DocumentTypeCreateData(BaseSchemaStruct):
    catalogus: str
    omschrijving: str
    vertrouwelijkheidaanduiding: Vertrouwelijkheidaanduiding
    begin_geldigheid: date
    informatieobjectcategorie: str
    einde_geldigheid: date | None | UnsetType = UNSET
    trefwoord: Sequence[str] | UnsetType = UNSET
    omschrijving_generiek: InformatieObjectTypeOmschrijvingGeneriek | UnsetType = UNSET


class DocumentType(BaseSchemaStruct):
    url: str
    catalogus: str
    omschrijving: str
    vertrouwelijkheidaanduiding: Vertrouwelijkheidaanduiding
    begin_geldigheid: date
    einde_geldigheid: date | None = None
    concept: bool
    besluittypen: Sequence[str]
    informatieobjectcategorie: str
    trefwoord: Sequence[str] = ()
    omschrijving_generiek: InformatieObjectTypeOmschrijvingGeneriek | None = None
    zaaktypen: Sequence[str]
    begin_object: date | None
    einde_object: date | None


class CaseTypeDocumentTypeCreateData(BaseSchemaStruct):
    zaaktype: str
    informatieobjecttype: str
    volgnummer: int
    richting: Richting
    statustype: str | None | UnsetType = UNSET


class CaseTypeDocumentType(BaseSchemaStruct):
    url: str
    zaaktype: str
    zaaktype_identificatie: str
    informatieobjecttype: str
    volgnummer: int
    richting: Richting
    statustype: str | None = None
    catalogus: str


class StatusTypeListParams(PaginationParams):
    datum_geldigheid: date | UnsetType = UNSET
    status: ConceptStatus | UnsetType = UNSET
    zaaktype: str | UnsetType = UNSET
    zaaktype_identificatie: str | UnsetType = UNSET


class StatusTypeCreateData(BaseSchemaStruct):
    zaaktype: str
    omschrijving: str
    volgnummer: int
    omschrijving_generiek: str | UnsetType = UNSET
    statustekst: str | UnsetType = UNSET
    informeren: bool | UnsetType = UNSET
    doorlooptijd: str | None | UnsetType = UNSET
    toelichting: str | None | UnsetType = UNSET
    checklistitem_statustype: Sequence[CheckListItem] | UnsetType = UNSET
    begin_geldigheid: date | None | UnsetType = UNSET
    einde_geldigheid: date | None | UnsetType = UNSET


class StatusType(BaseSchemaStruct):
    url: str
    omschrijving: str
    omschrijving_generiek: str = ""
    statustekst: str = ""
    zaaktype: str
    zaaktype_identificatie: str
    volgnummer: int
    is_eindstatus: bool
    informeren: bool = False
    doorlooptijd: str | None = None
    toelichting: str | None = None
    checklistitem_statustype: Sequence[CheckListItem] = ()
    catalogus: str
    eigenschappen: Sequence[str]
    zaakobjecttypen: Sequence[str]
    begin_geldigheid: date | None = None
    einde_geldigheid: date | None = None
    begin_object: date | None
    einde_object: date | None


class ResultTypeListParams(PaginationParams):
    datum_geldigheid: date | UnsetType = UNSET
    status: ConceptStatus | UnsetType = UNSET
    zaaktype: str | UnsetType = UNSET
    zaaktype_identificatie: str | UnsetType = UNSET


class ResultTypeCreateData(BaseSchemaStruct):
    zaaktype: str
    omschrijving: str
    resultaattypeomschrijving: str
    """
    URL of the generic result type description in the Selectielijst API.
    """
    selectielijstklasse: str
    """
    URL of the result in the Selectielijst API. It must belong to the
    ``selectielijst_procestype`` of the case type.
    """
    toelichting: str | UnsetType = UNSET
    archiefnominatie: Archiefnominatie | Literal[""] | UnsetType = UNSET
    archiefactietermijn: str | None | UnsetType = UNSET
    brondatum_archiefprocedure: BrondatumArchiefprocedure | None | UnsetType = UNSET
    procesobjectaard: str | UnsetType = UNSET
    indicatie_specifiek: bool | None | UnsetType = UNSET
    procestermijn: str | None | UnsetType = UNSET
    besluittypen: Sequence[str] | UnsetType = UNSET
    informatieobjecttypen: Sequence[str] | UnsetType = UNSET
    begin_geldigheid: date | None | UnsetType = UNSET
    einde_geldigheid: date | None | UnsetType = UNSET


class ResultType(BaseSchemaStruct):
    url: str
    zaaktype: str
    zaaktype_identificatie: str
    omschrijving: str
    resultaattypeomschrijving: str
    omschrijving_generiek: str
    selectielijstklasse: str
    toelichting: str = ""
    archiefnominatie: Archiefnominatie | Literal[""] = ""
    archiefactietermijn: str | None = None
    brondatum_archiefprocedure: BrondatumArchiefprocedure | None = None
    procesobjectaard: str = ""
    indicatie_specifiek: bool | None = None
    procestermijn: str | None = None
    catalogus: str
    besluittypen: Sequence[str] = ()
    besluittype_omschrijving: Sequence[str]
    informatieobjecttypen: Sequence[str] = ()
    informatieobjecttype_omschrijving: Sequence[str]
    begin_geldigheid: date | None = None
    einde_geldigheid: date | None = None
    begin_object: date | None
    einde_object: date | None


class RoleTypeListParams(PaginationParams):
    datum_geldigheid: date | UnsetType = UNSET
    omschrijving: str | UnsetType = UNSET
    omschrijving_generiek: RolOmschrijvingGeneriek | UnsetType = UNSET
    status: ConceptStatus | UnsetType = UNSET
    zaaktype: str | UnsetType = UNSET
    zaaktype_identificatie: str | UnsetType = UNSET


class RoleTypeCreateData(BaseSchemaStruct):
    zaaktype: str
    omschrijving: str
    omschrijving_generiek: RolOmschrijvingGeneriek
    begin_geldigheid: date | None | UnsetType = UNSET
    einde_geldigheid: date | None | UnsetType = UNSET


class RoleType(BaseSchemaStruct):
    url: str
    zaaktype: str
    zaaktype_identificatie: str
    omschrijving: str
    omschrijving_generiek: RolOmschrijvingGeneriek
    catalogus: str
    begin_geldigheid: date | None = None
    einde_geldigheid: date | None = None
    begin_object: date | None
    einde_object: date | None
