Testing
=======

.. todo:: add docker compose

Unit tests are performed against a local Open Zaak container, see the ``docker-compose.yaml``
in the root of the repository for details. You also find the exact version that the client
was tested against there.

.. tip::

    When making changes to the test data for the containers, make sure to commit them so that
    other developers have the same data when re-recording cassettes.

Unit tests make use of VCR for capturing the real API responses. When adding tests, you
will need to make sure the initial cassettes can be recorded. For this, you need to spin
up the containers with the Open Zaak service(s).

In the root of the repository:

.. code-block:: bash

    docker compose up

When you're changing existing code, or testing a newer version of Open Zaak, you
should also re-record the VCR cassettes. This too requires the containers to be running -
see the command above on how to do this.

There's a convenience script to re-record cassettes, in the root of the repository:

.. code-block:: bash

    ./re_record_vcr_cassettes.sh
