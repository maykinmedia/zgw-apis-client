"""
Structs for the Zaken API.
"""

from collections.abc import Sequence
from datetime import date, datetime
from typing import Any, ClassVar, Literal
from uuid import UUID

from msgspec import UNSET, UnsetType

from .base import BaseSchemaStruct, PaginationParams
from .common import (
    Archiefnominatie,
    RolOmschrijvingGeneriek,
    Vertrouwelijkheidaanduiding,
)

type Archiefstatus = Literal[
    "nog_te_archiveren",
    "gearchiveerd",
    "gearchiveerd_procestermijn_onbekend",
    "overgedragen",
]

type Betalingsindicatie = Literal[
    "", "nvt", "nog_niet", "gedeeltelijk", "geheel", "gefactureerd", "gecrediteerd"
]

type AardRelatieZaak = Literal["vervolg", "onderwerp", "bijdrage", "overig"]

type BetrokkeneType = Literal[
    "natuurlijk_persoon",
    "niet_natuurlijk_persoon",
    "vestiging",
    "organisatorische_eenheid",
    "medewerker",
]

type IndicatieMachtiging = Literal["", "gemachtigde", "machtiginggever"]


class ZaakKenmerk(BaseSchemaStruct):
    kenmerk: str
    bron: str


class Verlenging(BaseSchemaStruct):
    reden: str
    duur: str  # ISO 8601 duration


class Opschorting(BaseSchemaStruct):
    indicatie: bool
    reden: str
    eerdere_opschorting: bool = False


class RelevanteZaak(BaseSchemaStruct):
    url: str
    aard_relatie: AardRelatieZaak
    overige_relatie: str = ""
    toelichting: str = ""


class Processobject(BaseSchemaStruct):
    datumkenmerk: str
    identificatie: str
    objecttype: str
    registratie: str


class CaseListParams(PaginationParams):
    bronorganisatie: str | UnsetType = UNSET
    identificatie: str | UnsetType = UNSET
    zaaktype: str | UnsetType = UNSET
    archiefstatus: Archiefstatus | UnsetType = UNSET
    startdatum: date | UnsetType = UNSET
    startdatum__gte: date | UnsetType = UNSET
    startdatum__lte: date | UnsetType = UNSET
    einddatum__isnull: bool | UnsetType = UNSET
    rol__betrokkene_type: BetrokkeneType | UnsetType = UNSET
    rol__omschrijving_generiek: RolOmschrijvingGeneriek | UnsetType = UNSET
    rol__betrokkene_identificatie__medewerker__identificatie: str | UnsetType = UNSET
    status__statustype: str | UnsetType = UNSET
    ordering: str | UnsetType = UNSET


class CaseCreateData(BaseSchemaStruct):
    zaaktype: str
    bronorganisatie: str
    verantwoordelijke_organisatie: str
    startdatum: date
    identificatie: str | UnsetType = UNSET
    omschrijving: str | UnsetType = UNSET
    toelichting: str | UnsetType = UNSET
    registratiedatum: date | UnsetType = UNSET
    einddatum_gepland: date | None | UnsetType = UNSET
    uiterlijke_einddatum_afdoening: date | None | UnsetType = UNSET
    publicatiedatum: date | None | UnsetType = UNSET
    communicatiekanaal: str | UnsetType = UNSET
    communicatiekanaal_naam: str | UnsetType = UNSET
    producten_of_diensten: Sequence[str] | UnsetType = UNSET
    vertrouwelijkheidaanduiding: Vertrouwelijkheidaanduiding | UnsetType = UNSET
    betalingsindicatie: Betalingsindicatie | UnsetType = UNSET
    hoofdzaak: str | None | UnsetType = UNSET
    relevante_andere_zaken: Sequence[RelevanteZaak] | UnsetType = UNSET
    kenmerken: Sequence[ZaakKenmerk] | UnsetType = UNSET
    opdrachtgevende_organisatie: str | UnsetType = UNSET


class Case(BaseSchemaStruct):
    url: str
    uuid: UUID
    identificatie: str = ""
    bronorganisatie: str
    omschrijving: str = ""
    toelichting: str = ""
    zaaktype: str
    registratiedatum: date | None = None
    verantwoordelijke_organisatie: str
    startdatum: date
    einddatum: date | None
    einddatum_gepland: date | None = None
    uiterlijke_einddatum_afdoening: date | None = None
    publicatiedatum: date | None = None
    laatst_gemuteerd: datetime
    laatst_geopend: datetime | None = None
    communicatiekanaal: str = ""
    communicatiekanaal_naam: str = ""
    producten_of_diensten: Sequence[str] = ()
    vertrouwelijkheidaanduiding: Vertrouwelijkheidaanduiding | None = None
    betalingsindicatie: Betalingsindicatie = ""
    betalingsindicatie_weergave: str
    laatste_betaaldatum: datetime | None = None
    zaakgeometrie: dict[str, Any] | None = None
    """
    GeoJSON geometry, not modelled further.
    """
    verlenging: Verlenging | None = None
    opschorting: Opschorting | None = None
    selectielijstklasse: str = ""
    hoofdzaak: str | None = None
    deelzaken: Sequence[str]
    relevante_andere_zaken: Sequence[RelevanteZaak] = ()
    eigenschappen: Sequence[str]
    rollen: Sequence[str]
    status: str | None
    zaakinformatieobjecten: Sequence[str]
    zaakobjecten: Sequence[str]
    kenmerken: Sequence[ZaakKenmerk] = ()
    archiefnominatie: Archiefnominatie | Literal[""] | None = None
    archiefstatus: Archiefstatus | None = None
    archiefactiedatum: date | None = None
    resultaat: str | None
    opdrachtgevende_organisatie: str = ""
    processobjectaard: str = ""
    startdatum_bewaartermijn: date | None = None
    processobject: Processobject | None = None


class StatusListParams(PaginationParams):
    zaak: str | UnsetType = UNSET
    statustype: str | UnsetType = UNSET
    indicatie_laatst_gezette_status: bool | UnsetType = UNSET


class StatusCreateData(BaseSchemaStruct):
    zaak: str
    statustype: str
    datum_status_gezet: datetime
    statustoelichting: str | UnsetType = UNSET
    gezetdoor: str | None | UnsetType = UNSET
    """
    URL of the role that set the status.
    """


class Status(BaseSchemaStruct):
    url: str
    uuid: UUID
    zaak: str
    statustype: str
    datum_status_gezet: datetime
    statustoelichting: str = ""
    indicatie_laatst_gezette_status: bool
    gezetdoor: str | None = None
    zaakinformatieobjecten: Sequence[str]


class RoleListParams(PaginationParams):
    zaak: str | UnsetType = UNSET
    roltype: str | UnsetType = UNSET
    betrokkene: str | UnsetType = UNSET
    betrokkene_type: BetrokkeneType | UnsetType = UNSET
    omschrijving: str | UnsetType = UNSET
    omschrijving_generiek: RolOmschrijvingGeneriek | UnsetType = UNSET
    betrokkene_identificatie__medewerker__identificatie: str | UnsetType = UNSET


class ContactPersoonRol(BaseSchemaStruct):
    naam: str
    emailadres: str = ""
    functie: str = ""
    telefoonnummer: str = ""


class MedewerkerIdentificatie(BaseSchemaStruct):
    identificatie: str = ""
    achternaam: str = ""
    voorletters: str = ""
    voorvoegsel_achternaam: str = ""


# We only work with employees, so only EmployeeRole has a typed identification. The
# other types are there so roles added by other systems (e.g. the applicant) still load.
class BaseRole(BaseSchemaStruct, tag_field="betrokkeneType"):
    url: str
    uuid: UUID
    zaak: str
    betrokkene: str = ""
    afwijkende_naam_betrokkene: str = ""
    roltype: str
    omschrijving: str
    omschrijving_generiek: RolOmschrijvingGeneriek
    roltoelichting: str = ""
    registratiedatum: datetime
    indicatie_machtiging: IndicatieMachtiging = ""
    contactpersoon_rol: ContactPersoonRol | None = None
    statussen: Sequence[str]
    begin_geldigheid: date | None = None
    einde_geldigheid: date | None = None

    @property
    def betrokkene_type(self) -> BetrokkeneType:
        return self.__struct_config__.tag  # pyright: ignore[reportReturnType]


class EmployeeRole(BaseRole, tag="medewerker"):
    betrokkene_identificatie: MedewerkerIdentificatie | None = None


class NaturalPersonRole(BaseRole, tag="natuurlijk_persoon"):
    betrokkene_identificatie: dict[str, Any] | None = None


class NonNaturalPersonRole(BaseRole, tag="niet_natuurlijk_persoon"):
    betrokkene_identificatie: dict[str, Any] | None = None


class BranchRole(BaseRole, tag="vestiging"):
    betrokkene_identificatie: dict[str, Any] | None = None


class OrganisationalUnitRole(BaseRole, tag="organisatorische_eenheid"):
    betrokkene_identificatie: dict[str, Any] | None = None


type Role = (
    EmployeeRole
    | NaturalPersonRole
    | NonNaturalPersonRole
    | BranchRole
    | OrganisationalUnitRole
)


class EmployeeRoleCreateData(
    BaseSchemaStruct, tag_field="betrokkeneType", tag="medewerker"
):
    zaak: str
    roltype: str
    roltoelichting: str | UnsetType = UNSET
    betrokkene_identificatie: MedewerkerIdentificatie | UnsetType = UNSET
    betrokkene: str | UnsetType = UNSET
    afwijkende_naam_betrokkene: str | UnsetType = UNSET
    indicatie_machtiging: IndicatieMachtiging | UnsetType = UNSET
    contactpersoon_rol: ContactPersoonRol | None | UnsetType = UNSET
    begin_geldigheid: date | None | UnsetType = UNSET
    einde_geldigheid: date | None | UnsetType = UNSET

    betrokkene_type: ClassVar[BetrokkeneType] = "medewerker"


class CaseDocumentListParams(BaseSchemaStruct):
    zaak: str | UnsetType = UNSET
    informatieobject: str | UnsetType = UNSET


class CaseDocumentCreateData(BaseSchemaStruct):
    zaak: str
    informatieobject: str
    """
    URL of the document in the Documenten API.
    """
    titel: str | UnsetType = UNSET
    beschrijving: str | UnsetType = UNSET
    vernietigingsdatum: datetime | None | UnsetType = UNSET
    status: str | None | UnsetType = UNSET


class CaseDocument(BaseSchemaStruct):
    url: str
    uuid: UUID
    informatieobject: str
    zaak: str
    aard_relatie_weergave: str
    titel: str = ""
    beschrijving: str = ""
    registratiedatum: datetime
    vernietigingsdatum: datetime | None = None
    status: str | None = None
