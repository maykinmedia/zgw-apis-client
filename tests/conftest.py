import pytest

from tests.helpers import OpenZaakServiceManager


def pytest_addoption(parser):
    parser.addoption(
        "--with-openzaak-service",
        action="store_true",
        default=False,
        help="Whether to seed a fresh Open Zaak Docker instance for each test",
    )


@pytest.fixture(scope="session", autouse=True)
def openzaak_service_singleton(request):
    # Depending on whether we're working with a live service or not, we either
    # spawn the service and yield the running service, or simply return a
    # regular instance for the purposes of using the client factory in the
    # client fixture. We split the fixtures up because the service singleton
    # should be session-scoped, spawning the service at the start of the run
    # and tearing it down at completion of the run.
    #
    # The client fixture below, by cotrast, should reset the database state
    # for each test.
    service = OpenZaakServiceManager()
    if request.config.getoption("--with-openzaak-service"):
        with service.live_service() as running_service:
            yield running_service
    else:
        yield service


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "match_on": [
            "method",
            "scheme",
            "host",
            "port",
            "path",
            "query",
            # "body",
        ],
    }
