"""
Resources of the Zaken API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

import msgspec

from ..structs.base import PaginatedResponseBody
from ..structs.cases import (
    Case,
    CaseCreateData,
    CaseDocument,
    CaseDocumentCreateData,
    CaseDocumentListParams,
    CaseListParams,
    EmployeeRoleCreateData,
    Role,
    RoleListParams,
    Status,
    StatusCreateData,
    StatusListParams,
)
from .base import BaseResource

if TYPE_CHECKING:
    # only used in the BaseResource[...] type hint
    from ..clients import CasesClient  # noqa: F401

CRS = "EPSG:4326"
"""
The Zaken API refuses requests on cases without this header, even when there's no
geometry.
"""


class CaseResource(BaseResource["CasesClient"]):
    base_path: ClassVar[str] = "zaken"

    def list(
        self, *, params: CaseListParams | None = None
    ) -> PaginatedResponseBody[Case]:
        return self._list_resources(
            PaginatedResponseBody[Case], params=params, headers={"Accept-Crs": CRS}
        )

    def retrieve(self, identifier: str | UUID) -> Case:
        return self._retrieve_resource(identifier, Case, headers={"Accept-Crs": CRS})

    def create(self, data: CaseCreateData) -> Case:
        """
        The case type has to be published.
        """
        return self._create_resource(
            data, Case, headers={"Accept-Crs": CRS, "Content-Crs": CRS}
        )


class StatusResource(BaseResource["CasesClient"]):
    base_path: ClassVar[str] = "statussen"

    def list(
        self, *, params: StatusListParams | None = None
    ) -> PaginatedResponseBody[Status]:
        return self._list_resources(PaginatedResponseBody[Status], params=params)

    def retrieve(self, identifier: str | UUID) -> Status:
        return self._retrieve_resource(identifier, Status)

    def create(self, data: StatusCreateData) -> Status:
        return self._create_resource(data, Status)


class RoleResource(BaseResource["CasesClient"]):
    base_path: ClassVar[str] = "rollen"

    def list(
        self, *, params: RoleListParams | None = None
    ) -> PaginatedResponseBody[Role]:
        return self._list_resources(PaginatedResponseBody[Role], params=params)

    def retrieve(self, identifier: str | UUID) -> Role:
        response = self._get(self._detail_path(identifier))
        # betrokkeneType decides which Role class comes back
        return msgspec.convert(response.json(), type=Role)

    def create(self, data: EmployeeRoleCreateData) -> Role:
        """
        Only employee roles for now.
        """
        response = self._post(self.base_path, data=msgspec.to_builtins(data))
        return msgspec.convert(response.json(), type=Role)


class CaseDocumentResource(BaseResource["CasesClient"]):
    """
    Links a case to a document in the Documenten API.
    """

    base_path: ClassVar[str] = "zaakinformatieobjecten"

    def list(
        self, *, params: CaseDocumentListParams | None = None
    ) -> list[CaseDocument]:
        """
        Not paginated, so filter on ``zaak`` or you get everything.
        """
        return self._list_resources(list[CaseDocument], params=params)

    def create(self, data: CaseDocumentCreateData) -> CaseDocument:
        """
        The case type has to allow the document's type.
        """
        return self._create_resource(data, CaseDocument)
