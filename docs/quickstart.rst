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
:class:`~zgw_apis_client.CasesClient` (Zaken API) and
:class:`~zgw_apis_client.DocumentsClient` (Documenten API). Each one gives access to the
resources of its API, like ``client.case`` or ``client.case_type``.

In a Django project, configure the clients from a
`zgw-consumers <https://zgw-consumers.readthedocs.io/>`_ service, which takes care of
the authentication (it generates the JWT from the client ID and secret):

.. code-block:: python

    from zgw_consumers.client import build_client

    from zgw_apis_client import CasesClient
    from zgw_apis_client.structs.cases import CaseListParams

    with build_client(service, client_factory=CasesClient) as client:
        page = client.case.list(params=CaseListParams(zaaktype=case_type_url))

    for case in page.results:
        print(case.identificatie, case.omschrijving)

Outside of Django, pass the API root and a ready-made token:

.. code-block:: python

    from zgw_apis_client import CatalogiClient

    with CatalogiClient(
        "https://openzaak.example.com/catalogi/api/v1/",
        bearer_token=token,
    ) as client:
        case_type = client.case_type.retrieve(case.zaaktype)

``retrieve`` takes a UUID or a full URL, so you can pass e.g. ``case.zaaktype``
directly.

Naming
------

Class names are in English (``Case``, ``CaseType``...), while the attributes follow the
API and are in Dutch, converted to snake case (``zaaktype``, ``startdatum``...). Query
parameters with lookups keep their double underscores
(``rol__betrokkene_identificatie__medewerker__identificatie``).

Roles
-----

Roles are returned as one of the role structs, depending on the type of the person or
organisation involved. Only employees (:class:`~zgw_apis_client.structs.cases.EmployeeRole`)
are modelled in detail; for the other types, ``betrokkene_identificatie`` is a plain
dict.
