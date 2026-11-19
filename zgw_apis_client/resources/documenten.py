from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from ..structs.base import PaginatedResponseBody
from ..structs.documenten import (
    EnkelvoudigInformatieObject,
    EnkelvoudigInformatieObjectCreateData,
    EnkelvoudigInformatieObjectListParams,
)
from .base import BaseResource

if TYPE_CHECKING:
    # only used in the BaseResource[...] type hint
    from ..clients import DocumentenClient  # noqa: F401


class EnkelvoudigInformatieObjectResource(BaseResource["DocumentenClient"]):
    base_path: ClassVar[str] = "enkelvoudiginformatieobjecten"

    def list(
        self, *, params: EnkelvoudigInformatieObjectListParams | None = None
    ) -> PaginatedResponseBody[EnkelvoudigInformatieObject]:
        return self._list_resources(
            PaginatedResponseBody[EnkelvoudigInformatieObject], params=params
        )

    def retrieve(self, *, identifier: str | UUID) -> EnkelvoudigInformatieObject:
        """
        Returns the latest version.
        """
        return self._retrieve_resource(identifier, EnkelvoudigInformatieObject)

    def create(
        self, *, data: EnkelvoudigInformatieObjectCreateData
    ) -> EnkelvoudigInformatieObject:
        """
        Pass the file content base64-encoded in ``inhoud``.
        """
        return self._create_resource(data, EnkelvoudigInformatieObject)
