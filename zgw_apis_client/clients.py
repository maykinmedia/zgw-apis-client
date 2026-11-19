from collections.abc import MutableMapping

from ape_pie import APIClient
from ape_pie.typing import ConfigAdapter

from .resources.catalogi import (
    CatalogusResource,
    InformatieObjectTypeResource,
    ResultaatTypeResource,
    RolTypeResource,
    StatusTypeResource,
    ZaakTypeInformatieObjectTypeResource,
    ZaakTypeResource,
)
from .resources.documenten import EnkelvoudigInformatieObjectResource
from .resources.zaken import (
    RolResource,
    StatusResource,
    ZaakInformatieObjectResource,
    ZaakResource,
)


class ZGWClient(APIClient):
    """
    Base client for the ZGW APIs.

    ``base_url`` is the API root, e.g. ``https://open-zaak.example.com/zaken/api/v1/``.

    In a Django project, use :meth:`configure_from` with a zgw-consumers service, which
    takes care of the (JWT) authentication. Alternatively, pass a ready-made token as
    ``bearer_token``.
    """

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


class CatalogiClient(ZGWClient):
    """
    Client class for the catalogue API ("Catalogi API").
    """

    catalogus = CatalogusResource()
    zaaktype = ZaakTypeResource()
    zaaktype_informatieobjecttype = ZaakTypeInformatieObjectTypeResource()
    informatieobjecttype = InformatieObjectTypeResource()
    statustype = StatusTypeResource()
    resultaattype = ResultaatTypeResource()
    roltype = RolTypeResource()


class ZakenClient(ZGWClient):
    """
    Client class for the cases API ("Zaken API").
    """

    zaak = ZaakResource()
    status = StatusResource()
    rol = RolResource()
    zaakinformatieobject = ZaakInformatieObjectResource()


class DocumentenClient(ZGWClient):
    """
    Client class for the documents API ("Documenten API").
    """

    enkelvoudiginformatieobject = EnkelvoudigInformatieObjectResource()
