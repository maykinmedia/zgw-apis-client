Testing
=======

The tests use VCR cassettes with the real API responses of Open Zaak, so the test
suite runs without any service. See the ``docker-compose.yaml`` in the root of the
repository for the exact Open Zaak version the client is tested against.

There is no seed data: every test starts with an empty Open Zaak and creates the data
it needs through the client itself. ``tests/data.py`` has builders for the catalogue
data (a published case type needs quite some related data); everything a test asserts
on is created in the test. Use fixed dates in test data, the cassettes replay the
responses of the day they were recorded.

Recording cassettes
-------------------

When adding tests, changing existing code or testing a newer version of Open Zaak, you
need to record the cassettes against a running Open Zaak. Recording needs internet
access, because Open Zaak validates the Selectielijst references of case types against
the public Selectielijst API.

The quickest way while working on tests is to start the stack once and keep it running:

.. code-block:: bash

    docker compose -p openzaak-api-test up -d --wait
    pytest --reuse-openzaak-service --record-mode=all

The database is reset before each test, and the API credentials from
``docker/open-zaak/setup_configuration/`` are applied again.

To re-record all cassettes against a fresh stack, which is spawned and removed by the
test run, use the convenience script in the root of the repository:

.. code-block:: bash

    ./re_record_vcr_cassettes.sh

Authentication
--------------

``tests.helpers.generate_jwt`` creates a JWT for the test credentials, with the same
claims zgw-consumers uses:

.. code-block:: python

    from tests.helpers import ZAKEN_API_ROOT, generate_jwt
    from zgw_apis_client import CasesClient

    client = CasesClient(ZAKEN_API_ROOT, bearer_token=generate_jwt())
