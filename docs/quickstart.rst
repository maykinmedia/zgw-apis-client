==========
Quickstart
==========

Installation
============

* Install from PyPI using ``uv``:

   .. code-block:: bash

      uv pip install zgw-apis-client

Requirements
============

* API root URLs where each relevant API (Catalogi, Zaken, Documenten) is hosted
* Client ID/Secret for each API with the relevant read/write permissions

The client is developed against the API versions implemented by Open Zaak 1.31:
Catalogi API 1.3, Zaken API 1.5 and Documenten API 1.6.

Usage
=====

There is a client per API: :class:`~zgw_apis_client.CatalogiClient`,
:class:`~zgw_apis_client.ZakenClient` (Zaken API) and
:class:`~zgw_apis_client.DocumentenClient` (Documenten API). Each one gives access to
the resources of its API, like ``client.zaak`` or ``client.zaaktype``.

In a Django project, configure the clients from a
`zgw-consumers <https://zgw-consumers.readthedocs.io/>`_ service, which takes care of
the authentication (it generates the JWT from the client ID and secret):

.. code-block:: python

    from zgw_consumers.client import build_client

    from zgw_apis_client import ZakenClient
    from zgw_apis_client.structs.zaken import ZaakListParams

    with build_client(service, client_factory=ZakenClient) as client:
        page = client.zaak.list(params=ZaakListParams(zaaktype=zaaktype_url))

    for zaak in page.results:
        print(zaak.identificatie, zaak.omschrijving)

Outside of Django, pass the API root and a ready-made token:

.. code-block:: python

    from zgw_apis_client import CatalogiClient

    with CatalogiClient(
        "https://openzaak.example.com/catalogi/api/v1/",
        bearer_token=token,
    ) as client:
        zaaktype = client.zaaktype.retrieve(identifier=zaak.zaaktype)

``retrieve`` takes a UUID or a full URL, so you can pass e.g. ``zaak.zaaktype``
directly.

Naming
------

Names follow the API and are in Dutch: classes use the API's resource names (``Zaak``,
``ZaakType``, ``EnkelvoudigInformatieObject``...) and attributes are converted to snake
case (``zaaktype``, ``startdatum``...). Query
parameters with lookups keep their double underscores
(``rol__betrokkene_identificatie__medewerker__identificatie``).

Rollen
------

Roles are returned as one of the ``Rol`` structs, depending on the type of the person or
organisation involved. Only employees (:class:`~zgw_apis_client.structs.zaken.MedewerkerRol`)
are modelled in detail; for the other types, ``betrokkene_identificatie`` is a plain
dict.
