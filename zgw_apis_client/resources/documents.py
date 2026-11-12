from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from ..structs.base import PaginatedResponseBody
from ..structs.documents import Document, DocumentCreateData, DocumentListParams
from .base import BaseResource

if TYPE_CHECKING:
    # only used in the BaseResource[...] type hint
    from ..clients import DocumentsClient  # noqa: F401


class DocumentResource(BaseResource["DocumentsClient"]):
    base_path: ClassVar[str] = "enkelvoudiginformatieobjecten"

    def list(
        self, *, params: DocumentListParams | None = None
    ) -> PaginatedResponseBody[Document]:
        return self._list_resources(PaginatedResponseBody[Document], params=params)

    def retrieve(self, identifier: str | UUID) -> Document:
        """
        Returns the latest version.
        """
        return self._retrieve_resource(identifier, Document)

    def create(self, data: DocumentCreateData) -> Document:
        """
        Pass the file content base64-encoded in ``inhoud``.
        """
        return self._create_resource(data, Document)
