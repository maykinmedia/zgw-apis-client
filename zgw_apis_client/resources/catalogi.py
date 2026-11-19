"""
Resources of the Catalogi API.

We mostly read from this API. Create and publish are here so tests can set up their
own case types.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from ..structs.base import PaginatedResponseBody
from ..structs.catalogi import (
    Catalogus,
    CatalogusCreateData,
    InformatieObjectType,
    InformatieObjectTypeCreateData,
    InformatieObjectTypeListParams,
    ResultaatType,
    ResultaatTypeCreateData,
    ResultaatTypeListParams,
    RolType,
    RolTypeCreateData,
    RolTypeListParams,
    StatusType,
    StatusTypeCreateData,
    StatusTypeListParams,
    ZaakType,
    ZaakTypeCreateData,
    ZaakTypeInformatieObjectType,
    ZaakTypeInformatieObjectTypeCreateData,
    ZaakTypeListParams,
)
from .base import BaseResource

if TYPE_CHECKING:
    # only used in the BaseResource[...] type hint
    from ..clients import CatalogiClient  # noqa: F401


class CatalogusResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "catalogussen"

    def retrieve(self, *, identifier: str | UUID) -> Catalogus:
        return self._retrieve_resource(identifier, Catalogus)

    def create(self, *, data: CatalogusCreateData) -> Catalogus:
        return self._create_resource(data, Catalogus)


class ZaakTypeResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "zaaktypen"

    def list(
        self, *, params: ZaakTypeListParams | None = None
    ) -> PaginatedResponseBody[ZaakType]:
        """
        Concept case types are left out unless you filter on ``status``.
        """
        return self._list_resources(PaginatedResponseBody[ZaakType], params=params)

    def retrieve(self, *, identifier: str | UUID) -> ZaakType:
        return self._retrieve_resource(identifier, ZaakType)

    def create(self, *, data: ZaakTypeCreateData) -> ZaakType:
        """
        New case types are concepts. Publish them before creating cases.
        """
        return self._create_resource(data, ZaakType)

    def publish(self, *, identifier: str | UUID) -> ZaakType:
        """
        Open Zaak only publishes a case type with at least two status types, a result
        type, a role type, and published document types.
        """
        response = self._post(f"{self._detail_path(identifier)}/publish")
        return self.process_response(response, ZaakType)


class InformatieObjectTypeResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "informatieobjecttypen"

    def list(
        self, *, params: InformatieObjectTypeListParams | None = None
    ) -> PaginatedResponseBody[InformatieObjectType]:
        """
        Concept document types are left out unless you filter on ``status``.
        """
        return self._list_resources(
            PaginatedResponseBody[InformatieObjectType], params=params
        )

    def retrieve(self, *, identifier: str | UUID) -> InformatieObjectType:
        return self._retrieve_resource(identifier, InformatieObjectType)

    def create(self, *, data: InformatieObjectTypeCreateData) -> InformatieObjectType:
        """
        New document types are concepts and must be published before the case type.
        """
        return self._create_resource(data, InformatieObjectType)

    def publish(self, *, identifier: str | UUID) -> InformatieObjectType:
        response = self._post(f"{self._detail_path(identifier)}/publish")
        return self.process_response(response, InformatieObjectType)


class ZaakTypeInformatieObjectTypeResource(BaseResource["CatalogiClient"]):
    """
    Which document types can be added to cases of a case type.
    """

    base_path: ClassVar[str] = "zaaktype-informatieobjecttypen"

    def create(
        self, *, data: ZaakTypeInformatieObjectTypeCreateData
    ) -> ZaakTypeInformatieObjectType:
        return self._create_resource(data, ZaakTypeInformatieObjectType)


class StatusTypeResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "statustypen"

    def list(
        self, *, params: StatusTypeListParams | None = None
    ) -> PaginatedResponseBody[StatusType]:
        return self._list_resources(PaginatedResponseBody[StatusType], params=params)

    def retrieve(self, *, identifier: str | UUID) -> StatusType:
        return self._retrieve_resource(identifier, StatusType)

    def create(self, *, data: StatusTypeCreateData) -> StatusType:
        return self._create_resource(data, StatusType)


class ResultaatTypeResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "resultaattypen"

    def list(
        self, *, params: ResultaatTypeListParams | None = None
    ) -> PaginatedResponseBody[ResultaatType]:
        return self._list_resources(PaginatedResponseBody[ResultaatType], params=params)

    def retrieve(self, *, identifier: str | UUID) -> ResultaatType:
        return self._retrieve_resource(identifier, ResultaatType)

    def create(self, *, data: ResultaatTypeCreateData) -> ResultaatType:
        """
        Open Zaak checks the Selectielijst URLs against the public Selectielijst API.
        """
        return self._create_resource(data, ResultaatType)


class RolTypeResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "roltypen"

    def list(
        self, *, params: RolTypeListParams | None = None
    ) -> PaginatedResponseBody[RolType]:
        return self._list_resources(PaginatedResponseBody[RolType], params=params)

    def retrieve(self, *, identifier: str | UUID) -> RolType:
        return self._retrieve_resource(identifier, RolType)

    def create(self, *, data: RolTypeCreateData) -> RolType:
        return self._create_resource(data, RolType)
