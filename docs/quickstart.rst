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

* API root URLs where each relevant API (like Zaken API) is hosted
* Client ID/Secret for each API with the relevant read/write permissions

Usage
=====

To use the client, instantiate it with the connection parameters and call the methods on
the provided resources:

.. code-block:: python

    from zgw_apis_client import ZakenClient

    client = ZakenClient(
        base_url="https://zaken.example.com/api/v1/",
        client_id="foo",
        secret="supersecret",
    )

    with client:
        create_result = client.case.create(case_type=...)
    
    print(create_result)
