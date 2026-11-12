"""
Structs for the Documenten API.
"""

from collections.abc import Sequence
from datetime import date, datetime
from typing import Literal

from msgspec import UNSET, UnsetType

from .base import BaseSchemaStruct, PaginationParams
from .common import Vertrouwelijkheidaanduiding

type DocumentStatus = Literal[
    "in_bewerking", "ter_vaststelling", "definitief", "gearchiveerd"
]

type OndertekeningSoort = Literal["analoog", "digitaal", "pki"]

type IntegriteitAlgoritme = Literal[
    "crc_16",
    "crc_32",
    "crc_64",
    "fletcher_4",
    "fletcher_8",
    "fletcher_16",
    "fletcher_32",
    "hmac",
    "md5",
    "sha_1",
    "sha_256",
    "sha_512",
    "sha_3",
]


class Ondertekening(BaseSchemaStruct):
    soort: OndertekeningSoort | Literal[""]
    datum: date | None


class Integriteit(BaseSchemaStruct):
    algoritme: IntegriteitAlgoritme | Literal[""]
    waarde: str
    datum: date | None


class BestandsDeel(BaseSchemaStruct):
    url: str
    volgnummer: int
    omvang: int
    voltooid: bool
    lock: str = ""


class DocumentListParams(PaginationParams):
    bronorganisatie: str | UnsetType = UNSET
    identificatie: str | UnsetType = UNSET
    informatieobjecttype: str | UnsetType = UNSET
    titel: str | UnsetType = UNSET
    auteur: str | UnsetType = UNSET
    vertrouwelijkheidaanduiding: Vertrouwelijkheidaanduiding | UnsetType = UNSET
    locked: bool | UnsetType = UNSET
    ordering: str | UnsetType = UNSET


class DocumentCreateData(BaseSchemaStruct):
    bronorganisatie: str
    creatiedatum: date
    titel: str
    auteur: str
    taal: str
    """
    ISO 639-2/B language code, e.g. ``dut`` or ``eng``.
    """
    informatieobjecttype: str
    inhoud: str | None | UnsetType = UNSET
    """
    The base64-encoded file content.
    """
    bestandsnaam: str | UnsetType = UNSET
    bestandsomvang: int | None | UnsetType = UNSET
    formaat: str | UnsetType = UNSET
    identificatie: str | UnsetType = UNSET
    vertrouwelijkheidaanduiding: Vertrouwelijkheidaanduiding | UnsetType = UNSET
    status: DocumentStatus | UnsetType = UNSET
    link: str | UnsetType = UNSET
    beschrijving: str | UnsetType = UNSET
    ontvangstdatum: date | None | UnsetType = UNSET
    verzenddatum: date | None | UnsetType = UNSET
    indicatie_gebruiksrecht: bool | None | UnsetType = UNSET
    verschijningsvorm: str | UnsetType = UNSET
    trefwoorden: Sequence[str] | UnsetType = UNSET
    tonen_aan_initiator: bool | UnsetType = UNSET


class Document(BaseSchemaStruct):
    url: str
    identificatie: str = ""
    bronorganisatie: str
    creatiedatum: date
    titel: str
    vertrouwelijkheidaanduiding: Vertrouwelijkheidaanduiding | Literal[""] = ""
    auteur: str
    status: DocumentStatus | Literal[""] = ""
    formaat: str = ""
    taal: str
    versie: int
    begin_registratie: datetime
    bestandsnaam: str = ""
    inhoud: str | None = None
    """
    URL to download the file content.
    """
    bestandsomvang: int | None = None
    link: str = ""
    beschrijving: str = ""
    ontvangstdatum: date | None = None
    verzenddatum: date | None = None
    indicatie_gebruiksrecht: bool | None = None
    verschijningsvorm: str = ""
    ondertekening: Ondertekening | None = None
    integriteit: Integriteit | None = None
    informatieobjecttype: str
    locked: bool
    bestandsdelen: Sequence[BestandsDeel]
    trefwoorden: Sequence[str] = ()
    inhoud_is_vervallen: bool | None = None
    tonen_aan_initiator: bool = False
