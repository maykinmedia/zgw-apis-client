Welcome to ZGW APIs Client's documentation
==========================================

|build-status| |code-quality| |ruff| |coverage| |docs|

|python-versions| |pypi-version|

ZGW APIs Client is a strongly typed HTTP client library for the APIs implementing the
`ZGW APIs <https://vng-realisatie.github.io/gemma-zaken/>`_ standard.

Features
========

* Resource-driven Python API, e.g. ``cases_client.case.create(...)``
* Fully type-annotated for type safety and editor autocomplete support
* Built on top of requests and `msgspec <https://msgspec.dev/>`_

.. toctree::
   :maxdepth: 2

   quickstart
   developers
   testing
   changelog


.. |build-status| image:: https://github.com/maykinmedia/zgw-apis-client/actions/workflows/ci.yml/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/zgw-apis-client/actions/workflows/ci.yml

.. |code-quality| image:: https://github.com/maykinmedia/zgw-apis-client/actions/workflows/code-quality.yml/badge.svg
     :alt: Code quality checks
     :target: https://github.com/maykinmedia/zgw-apis-client/actions/workflows/code-quality.yml

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. |coverage| image:: https://codecov.io/gh/maykinmedia/zgw-apis-client/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/zgw-apis-client
    :alt: Coverage status

.. |docs| image:: https://readthedocs.org/projects/zgw-apis-client/badge/?version=latest
    :target: https://zgw-apis-client.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/zgw-apis-client.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/zgw-apis-client.svg
    :target: https://pypi.org/project/zgw-apis-client/
