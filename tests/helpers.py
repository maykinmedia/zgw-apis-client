import logging
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

import requests

CURRENT_DIR = Path(__file__).resolve()
BASE_DIR = Path(__file__).parent.parent.resolve()

logger = logging.getLogger(__name__)


class OpenZaakServiceManager:
    _in_server_context: bool = False
    _django_service_name: str = "web"
    _api_root: str = "http://localhost:8339"
    _docker_compose_project_name: str = "openzaak-api-test"
    _docker_compose_path: Path = BASE_DIR / "docker-compose.yaml"

    def _docker_compose(
        self,
        *args: str,
        check: bool = True,
        input: str | None = None,
    ):
        input_data = {"text": True, "input": input} if input else {}
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
                **input_data,
            )
        except subprocess.CalledProcessError as exc:
            logger.exception(
                "Unable to execute command. stderr: %s, stdout: %s",
                exc.stderr,
                exc.stdout,
            )
            raise

    def _manage_py(
        self,
        *args: str,
        input: str | None = None,
    ):
        self._docker_compose(
            "run",
            "--rm",
            self._django_service_name,
            "python",
            "src/manage.py",
            *args,
            input=input,
        )

    def _service_teardown(self):
        self._docker_compose("kill", check=False)
        self._docker_compose("down", "-v")
        self._docker_compose("rm", "-f")

    def _service_init(self):
        self._docker_compose("up", "-d")
        self._wait_for_response()
        self._manage_py("migrate")

    def reset_db_state(self):
        self._manage_py("flush", "--no-input")
        # self._load_fixture_from_json_string(self._generate_token_fixture())

    def _load_fixture_from_json_string(self, fixture: str):
        self._manage_py(
            "loaddata",
            "--format",
            "json",
            "-",  # i.e. stdin
            input=fixture,
        )

    def _wait_for_response(self, interval=0.5, max_wait=60):
        start_time = time.time()
        while True:
            try:
                response = requests.get(self._api_root)
                return response
            except requests.RequestException:
                logger.debug("Exception while checking for liveness", exc_info=True)
                elapsed_time = time.time() - start_time
                if elapsed_time > max_wait:
                    logger.info("Max wait time exceeded.")
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
    def clean_state(self):
        """Yield a client configured to talk a live OpenZaak service.

        Note that this requires the live server to have been spawned,
        either imperatively:

            service.setUp()
            with service.clean_state() as client:
                client.do_stuff()

            service.tearDown()

        ... or using the live_service() context manager:

            with service.live_server_manager() as live_service:
                with live_service.clean_state() as client:
                    client.do_something()

        """
        if not self._in_server_context:
            raise RuntimeError(
                "You must execute this context within the server context"
            )

        def clean_state_manager(*args, **kwds):
            self.reset_db_state()
            yield

        return clean_state_manager()

    @contextmanager
    def live_service(self):
        """Context manager to spawn a live OpenZaak service and clean it up.

        You will commonly nest a clean_state() context manager within the
        live_service block, for instance:

            with service.live_server_manager() as live_service:
                with live_service.clean_state() as client:
                    client.do_something()
        """

        def live_server_manager(*args, **kwds):
            try:
                self.setUp()
                yield self
            finally:
                self.tearDown()

        return live_server_manager()
