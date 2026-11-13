"""
Literals rather than Enums: a lot of fields also allow ``""``, and msgspec only allows
one str-like type in a union.
"""

from typing import Literal

type Vertrouwelijkheidaanduiding = Literal[
    "openbaar",
    "beperkt_openbaar",
    "intern",
    "zaakvertrouwelijk",
    "vertrouwelijk",
    "confidentieel",
    "geheim",
    "zeer_geheim",
]

type Archiefnominatie = Literal["blijvend_bewaren", "vernietigen"]

type RolOmschrijvingGeneriek = Literal[
    "adviseur",
    "behandelaar",
    "belanghebbende",
    "beslisser",
    "initiator",
    "klantcontacter",
    "zaakcoordinator",
    "mede_initiator",
]
"""
Generic description of a role (type), e.g. ``behandelaar`` for the case handler.
"""
