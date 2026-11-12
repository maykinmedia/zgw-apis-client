import pytest

from tests.helpers import (
    CATALOGI_API_ROOT,
    DOCUMENTEN_API_ROOT,
    ZAKEN_API_ROOT,
    OpenZaakServiceManager,
    generate_jwt,
)
from zgw_apis_client import CasesClient, CatalogiClient, DocumentsClient


def pytest_addoption(parser):
    parser.addoption(
        "--with-openzaak-service",
        action="store_true",
        default=False,
        help=(
            "Spawn a fresh Open Zaak Docker stack for the test run, and reset its "
            "database before each test. Needed to (re-)record the VCR cassettes."
        ),
    )
    parser.addoption(
        "--reuse-openzaak-service",
        action="store_true",
        default=False,
        help=(
            "Like --with-openzaak-service, but use an Open Zaak stack that is already "
            "running (`docker compose -p openzaak-api-test up -d --wait`)."
        ),
    )


@pytest.fixture(scope="session")
def openzaak_service(request):
    """
    ``None`` when replaying cassettes.
    """
    if request.config.getoption("--reuse-openzaak-service"):
        yield OpenZaakServiceManager()
        return

    if not request.config.getoption("--with-openzaak-service"):
        yield None
        return

    with OpenZaakServiceManager().live_service() as service:
        yield service


@pytest.fixture(autouse=True)
def clean_openzaak_state(openzaak_service: OpenZaakServiceManager | None):
    if openzaak_service is not None:
        openzaak_service.reset_db_state()


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
        ],
        "filter_headers": ["authorization"],
    }


@pytest.fixture
def catalogi_client():
    with CatalogiClient(CATALOGI_API_ROOT, bearer_token=generate_jwt()) as client:
        yield client


@pytest.fixture
def cases_client():
    with CasesClient(ZAKEN_API_ROOT, bearer_token=generate_jwt()) as client:
        yield client


@pytest.fixture
def documents_client():
    with DocumentsClient(DOCUMENTEN_API_ROOT, bearer_token=generate_jwt()) as client:
        yield client
