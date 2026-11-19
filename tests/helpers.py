import logging
import subprocess
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import jwt
import requests

BASE_DIR = Path(__file__).parent.parent.resolve()

OPENZAAK_ROOT = "http://localhost:8339"
CATALOGI_API_ROOT = f"{OPENZAAK_ROOT}/catalogi/api/v1/"
ZAKEN_API_ROOT = f"{OPENZAAK_ROOT}/zaken/api/v1/"
DOCUMENTEN_API_ROOT = f"{OPENZAAK_ROOT}/documenten/api/v1/"

# same as in docker/open-zaak/setup_configuration/data.yaml
CLIENT_ID = "test-client-id"
SECRET = "test-secret-for-the-zgw-apis-client-tests"

logger = logging.getLogger(__name__)


def generate_jwt(
    client_id: str = CLIENT_ID,
    secret: str = SECRET,
    *,
    user_id: str = "test-user",
    user_representation: str = "Test User",
    valid_for: int = 60 * 60,
) -> str:
    """
    Same claims as zgw-consumers' ``ZGWAuth``.
    """
    issued_at = int(time.time())
    payload = {
        "iss": client_id,
        "iat": issued_at,
        "exp": issued_at + valid_for,
        "client_id": client_id,
        "user_id": user_id,
        "user_representation": user_representation,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


class OpenZaakServiceManager:
    """
    Manage the Open Zaak docker compose stack defined in ``docker-compose.yaml``.

    Only used when (re-)recording the VCR cassettes, see ``docs/testing.rst``.
    """

    _django_service_name: str = "web"
    _docker_compose_project_name: str = "openzaak-api-test"
    _docker_compose_path: Path = BASE_DIR / "docker-compose.yaml"

    def __init__(self):
        self._in_server_context = False

    def _docker_compose(self, *args: str, check: bool = True):
        try:
            return subprocess.run(
                args=[
                    "docker",
                    "compose",
                    "-f",
                    str(self._docker_compose_path),
                    "-p",
                    self._docker_compose_project_name,
                    *args,
                ],
                check=check,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            logger.exception(
                "Unable to execute command. stderr: %s, stdout: %s",
                exc.stderr,
                exc.stdout,
            )
            raise

    def _manage_py(self, *args: str):
        self._docker_compose(
            "exec",
            "-T",
            self._django_service_name,
            "python",
            "src/manage.py",
            *args,
        )

    def _service_teardown(self):
        self._docker_compose("down", "--volumes", check=False)

    def _service_init(self):
        self._docker_compose("up", "--detach", "--wait")
        self._wait_for_response()

    def reset_db_state(self):
        """
        Remove all data, and re-apply the setup configuration.

        Flushing also removes the Selectielijst API configuration created by the
        Open Zaak migrations, so that is restored too.
        """
        self._manage_py("flush", "--no-input")
        for config_file in ("data.yaml", "selectielijst.yaml"):
            self._manage_py(
                "setup_configuration",
                "--yaml-file",
                f"setup_configuration/{config_file}",
            )

    def _wait_for_response(self, interval=0.5, max_wait=60):
        start_time = time.time()
        while True:
            try:
                return requests.get(OPENZAAK_ROOT)
            except requests.RequestException:
                logger.debug("Exception while checking for liveness", exc_info=True)
                elapsed_time = time.time() - start_time
                if elapsed_time > max_wait:
                    raise RuntimeError(
                        f"Maximum wait for service to be healthy exceeded: "
                        f"{elapsed_time} > {max_wait}"
                    ) from None
                time.sleep(interval)

    def setUp(self):
        if self._in_server_context:
            raise RuntimeError(
                "You cannot have multiple server contexts active at the same time"
            )

        self._in_server_context = True
        self._service_teardown()
        self._service_init()

    def tearDown(self):
        self._service_teardown()
        self._in_server_context = False

    @contextmanager
    def live_service(self) -> Iterator["OpenZaakServiceManager"]:
        try:
            self.setUp()
            yield self
        finally:
            self.tearDown()
