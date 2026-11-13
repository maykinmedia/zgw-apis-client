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
    CaseType,
    CaseTypeCreateData,
    CaseTypeDocumentType,
    CaseTypeDocumentTypeCreateData,
    CaseTypeListParams,
    Catalogue,
    CatalogueCreateData,
    DocumentType,
    DocumentTypeCreateData,
    DocumentTypeListParams,
    ResultType,
    ResultTypeCreateData,
    ResultTypeListParams,
    RoleType,
    RoleTypeCreateData,
    RoleTypeListParams,
    StatusType,
    StatusTypeCreateData,
    StatusTypeListParams,
)
from .base import BaseResource

if TYPE_CHECKING:
    # only used in the BaseResource[...] type hint
    from ..clients import CatalogiClient  # noqa: F401


class CatalogueResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "catalogussen"

    def retrieve(self, identifier: str | UUID) -> Catalogue:
        return self._retrieve_resource(identifier, Catalogue)

    def create(self, data: CatalogueCreateData) -> Catalogue:
        return self._create_resource(data, Catalogue)


class CaseTypeResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "zaaktypen"

    def list(
        self, *, params: CaseTypeListParams | None = None
    ) -> PaginatedResponseBody[CaseType]:
        """
        Concept case types are left out unless you filter on ``status``.
        """
        return self._list_resources(PaginatedResponseBody[CaseType], params=params)

    def retrieve(self, identifier: str | UUID) -> CaseType:
        return self._retrieve_resource(identifier, CaseType)

    def create(self, data: CaseTypeCreateData) -> CaseType:
        """
        New case types are concepts. Publish them before creating cases.
        """
        return self._create_resource(data, CaseType)

    def publish(self, identifier: str | UUID) -> CaseType:
        """
        Open Zaak only publishes a case type with at least two status types, a result
        type, a role type, and published document types.
        """
        response = self._post(f"{self._detail_path(identifier)}/publish")
        return self.process_response(response, CaseType)


class DocumentTypeResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "informatieobjecttypen"

    def list(
        self, *, params: DocumentTypeListParams | None = None
    ) -> PaginatedResponseBody[DocumentType]:
        """
        Concept document types are left out unless you filter on ``status``.
        """
        return self._list_resources(PaginatedResponseBody[DocumentType], params=params)

    def retrieve(self, identifier: str | UUID) -> DocumentType:
        return self._retrieve_resource(identifier, DocumentType)

    def create(self, data: DocumentTypeCreateData) -> DocumentType:
        """
        New document types are concepts and must be published before the case type.
        """
        return self._create_resource(data, DocumentType)

    def publish(self, identifier: str | UUID) -> DocumentType:
        response = self._post(f"{self._detail_path(identifier)}/publish")
        return self.process_response(response, DocumentType)


class CaseTypeDocumentTypeResource(BaseResource["CatalogiClient"]):
    """
    Which document types can be added to cases of a case type.
    """

    base_path: ClassVar[str] = "zaaktype-informatieobjecttypen"

    def create(self, data: CaseTypeDocumentTypeCreateData) -> CaseTypeDocumentType:
        return self._create_resource(data, CaseTypeDocumentType)


class StatusTypeResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "statustypen"

    def list(
        self, *, params: StatusTypeListParams | None = None
    ) -> PaginatedResponseBody[StatusType]:
        return self._list_resources(PaginatedResponseBody[StatusType], params=params)

    def retrieve(self, identifier: str | UUID) -> StatusType:
        return self._retrieve_resource(identifier, StatusType)

    def create(self, data: StatusTypeCreateData) -> StatusType:
        return self._create_resource(data, StatusType)


class ResultTypeResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "resultaattypen"

    def list(
        self, *, params: ResultTypeListParams | None = None
    ) -> PaginatedResponseBody[ResultType]:
        return self._list_resources(PaginatedResponseBody[ResultType], params=params)

    def retrieve(self, identifier: str | UUID) -> ResultType:
        return self._retrieve_resource(identifier, ResultType)

    def create(self, data: ResultTypeCreateData) -> ResultType:
        """
        Open Zaak checks the Selectielijst URLs against the public Selectielijst API.
        """
        return self._create_resource(data, ResultType)


class RoleTypeResource(BaseResource["CatalogiClient"]):
    base_path: ClassVar[str] = "roltypen"

    def list(
        self, *, params: RoleTypeListParams | None = None
    ) -> PaginatedResponseBody[RoleType]:
        return self._list_resources(PaginatedResponseBody[RoleType], params=params)

    def retrieve(self, identifier: str | UUID) -> RoleType:
        return self._retrieve_resource(identifier, RoleType)

    def create(self, data: RoleTypeCreateData) -> RoleType:
        return self._create_resource(data, RoleType)
