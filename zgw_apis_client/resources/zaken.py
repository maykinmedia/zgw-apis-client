"""
Resources of the Zaken API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

import msgspec

from ..structs.base import PaginatedResponseBody
from ..structs.zaken import (
    MedewerkerRolCreateData,
    Rol,
    RolListParams,
    Status,
    StatusCreateData,
    StatusListParams,
    Zaak,
    ZaakCreateData,
    ZaakInformatieObject,
    ZaakInformatieObjectCreateData,
    ZaakInformatieObjectListParams,
    ZaakListParams,
)
from .base import BaseResource

if TYPE_CHECKING:
    # only used in the BaseResource[...] type hint
    from ..clients import ZakenClient  # noqa: F401

CRS = "EPSG:4326"
"""
The Zaken API refuses requests on cases without this header, even when there's no
geometry.
"""


class ZaakResource(BaseResource["ZakenClient"]):
    base_path: ClassVar[str] = "zaken"

    def list(
        self, *, params: ZaakListParams | None = None
    ) -> PaginatedResponseBody[Zaak]:
        return self._list_resources(
            PaginatedResponseBody[Zaak], params=params, headers={"Accept-Crs": CRS}
        )

    def retrieve(self, *, identifier: str | UUID) -> Zaak:
        return self._retrieve_resource(identifier, Zaak, headers={"Accept-Crs": CRS})

    def create(self, *, data: ZaakCreateData) -> Zaak:
        """
        The case type has to be published.
        """
        return self._create_resource(
            data, Zaak, headers={"Accept-Crs": CRS, "Content-Crs": CRS}
        )


class StatusResource(BaseResource["ZakenClient"]):
    base_path: ClassVar[str] = "statussen"

    def list(
        self, *, params: StatusListParams | None = None
    ) -> PaginatedResponseBody[Status]:
        return self._list_resources(PaginatedResponseBody[Status], params=params)

    def retrieve(self, *, identifier: str | UUID) -> Status:
        return self._retrieve_resource(identifier, Status)

    def create(self, *, data: StatusCreateData) -> Status:
        return self._create_resource(data, Status)


class RolResource(BaseResource["ZakenClient"]):
    base_path: ClassVar[str] = "rollen"

    def list(
        self, *, params: RolListParams | None = None
    ) -> PaginatedResponseBody[Rol]:
        return self._list_resources(PaginatedResponseBody[Rol], params=params)

    def retrieve(self, *, identifier: str | UUID) -> Rol:
        response = self._get(self._detail_path(identifier))
        # betrokkeneType decides which Rol class comes back
        return msgspec.convert(response.json(), type=Rol)

    def create(self, *, data: MedewerkerRolCreateData) -> Rol:
        """
        Only employee roles for now.
        """
        response = self._post(self.base_path, data=msgspec.to_builtins(data))
        return msgspec.convert(response.json(), type=Rol)


class ZaakInformatieObjectResource(BaseResource["ZakenClient"]):
    """
    Links a case to a document in the Documenten API.
    """

    base_path: ClassVar[str] = "zaakinformatieobjecten"

    def list(
        self, *, params: ZaakInformatieObjectListParams | None = None
    ) -> list[ZaakInformatieObject]:
        """
        Not paginated, so filter on ``zaak`` or you get everything.
        """
        return self._list_resources(list[ZaakInformatieObject], params=params)

    def create(self, *, data: ZaakInformatieObjectCreateData) -> ZaakInformatieObject:
        """
        The case type has to allow the document's type.
        """
        return self._create_resource(data, ZaakInformatieObject)
