from __future__ import annotations

import copy
import logging
from collections.abc import Mapping
from typing import TYPE_CHECKING, ClassVar, Self
from uuid import UUID

import msgspec
import requests

if TYPE_CHECKING:
    from ..clients import ZGWClient


logger = logging.getLogger(__name__)


class BaseResource[C: ZGWClient]:
    """
    Base resource class wrapping the HTTP transport and msgspec conversion patterns.

    Every concrete resource should inherit from this class and specify the concrete
    client class that's expected:

    .. code-block::

        class MyResource(BaseResource[ExpectedClient]):
            def retrieve(self, ...) -> ...:
                ...
    """

    base_path: ClassVar[str] = ""

    _name: str = ""
    _http_client: C | None = None

    def __set_name__(self, owner: type[C], name: str) -> None:
        self._name = name

    def __get__(self, client: C | None, owner: type[C]) -> Self:
        # class attribute access
        if client is None:
            return self

        # bind the client
        bound = copy.copy(self)
        bound._http_client = client
        # Cache on the instance. Because this is a non-data descriptor
        # (no __set__), the instance attribute now shadows it, so later
        # accesses skip __get__ and return the same bound resource.
        client.__dict__[self._name] = bound

        return bound

    @property
    def http_client(self) -> C:
        if self._http_client is None:
            raise RuntimeError(
                f"{type(self).__name__} is not bound to a client; access it through a "
                "client instance."
            )
        return self._http_client

    @staticmethod
    def process_response[T](
        response: requests.Response,
        struct_type: type[T],
    ) -> T:
        """
        All the needed processing on the retrieved data.

        The JSON data is processed and converted to msgspec structs. This includes the
        validation of the incoming data.

        .. todo:: Implement proper error handling with response-shape aware structs.
        """
        response_data = response.json()
        # for now: assume no errors :)
        return msgspec.convert(response_data, type=struct_type)

    def _detail_path(self, identifier: str | UUID) -> str:
        # Accept a full URL too, since that's what you get in e.g. ``zaak.zaaktype``.
        # ape-pie checks that it's under the base URL.
        identifier = str(identifier)
        if identifier.startswith(("http://", "https://")):
            return identifier
        return f"{self.base_path}/{identifier}"

    def _list_resources[T](
        self,
        struct_type: type[T],
        *,
        params: msgspec.Struct | None = None,
        headers: Mapping | None = None,
    ) -> T:
        response = self._get(self.base_path, headers=headers, params=params)
        return self.process_response(response, struct_type)

    def _retrieve_resource[T](
        self,
        identifier: str | UUID,
        struct_type: type[T],
        *,
        headers: Mapping | None = None,
    ) -> T:
        response = self._get(self._detail_path(identifier), headers=headers)
        return self.process_response(response, struct_type)

    def _create_resource[T](
        self,
        data: msgspec.Struct,
        struct_type: type[T],
        *,
        headers: Mapping | None = None,
    ) -> T:
        response = self._post(
            self.base_path, headers=headers, data=msgspec.to_builtins(data)
        )
        return self.process_response(response, struct_type)

    def _get(
        self,
        path: str,
        headers: Mapping | None = None,
        params: msgspec.Struct | None = None,
    ) -> requests.Response:
        query_params = msgspec.to_builtins(params)
        response = self.http_client.request(
            "get", path, headers=headers, params=query_params
        )
        response.raise_for_status()
        return response

    def _post(
        self,
        path: str,
        headers: Mapping | None = None,
        params: msgspec.Struct | None = None,
        data: object = None,
    ) -> requests.Response:
        query_params = msgspec.to_builtins(params)
        response = self.http_client.request(
            "post",
            path,
            headers=headers,
            json=data,
            params=query_params,
        )
        response.raise_for_status()
        return response

    def _put(
        self,
        path: str,
        headers: Mapping | None = None,
        params: msgspec.Struct | None = None,
        data: object = None,
    ) -> requests.Response:
        query_params = msgspec.to_builtins(params)
        response = self.http_client.request(
            "put", path, headers=headers, json=data, params=query_params
        )
        response.raise_for_status()
        return response

    def _delete(
        self,
        path: str,
        headers: Mapping | None = None,
        params: msgspec.Struct | None = None,
    ) -> requests.Response:
        query_params = msgspec.to_builtins(params)
        response = self.http_client.request(
            "delete",
            path,
            headers=headers,
            params=query_params,
        )
        response.raise_for_status()
        return response

    def _patch(
        self,
        path: str,
        headers: Mapping | None = None,
        params: msgspec.Struct | None = None,
        data: object = None,
    ) -> requests.Response:
        query_params = msgspec.to_builtins(params)
        response = self.http_client.request(
            "patch",
            path,
            headers=headers,
            params=query_params,
            json=data,
        )
        response.raise_for_status()
        return response

    def _options(
        self,
        path: str,
        headers: Mapping | None = None,
        params: msgspec.Struct | None = None,
    ) -> requests.Response:
        query_params = msgspec.to_builtins(params)
        response = self.http_client.request(
            "options",
            path,
            headers=headers,
            params=query_params,
        )
        response.raise_for_status()
        return response
