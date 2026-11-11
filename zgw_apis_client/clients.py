from collections.abc import MutableMapping

from ape_pie import APIClient
from ape_pie.typing import ConfigAdapter

# from .resources.cases import (
#     CaseResource,
#     RoleResource,
# )


class ZGWClient(APIClient):
    def __init__(
        self,
        base_url: str,
        *,
        bearer_token: str = "",
        request_kwargs: MutableMapping[str, object] | None = None,
        **kwargs,
    ):
        if request_kwargs is None:
            request_kwargs = {}
        if "headers" not in request_kwargs:
            request_kwargs["headers"] = {}

        assert isinstance(request_kwargs["headers"], MutableMapping)

        if bearer_token:
            request_kwargs["headers"]["Authorization"] = f"Bearer {bearer_token}"

        super().__init__(base_url=base_url, request_kwargs=request_kwargs)  # pyright: ignore[reportArgumentType]

    @classmethod
    def configure_from(cls, adapter: ConfigAdapter, **kwargs):
        base_url = adapter.get_client_base_url()
        session_kwargs = adapter.get_client_session_kwargs()
        return cls(base_url, request_kwargs=session_kwargs, **kwargs)


class CasesClient(ZGWClient):
    """
    Client class for the cases API ("Zaken API").
    """

    # case = CaseResource()
    # role = RoleResource()
