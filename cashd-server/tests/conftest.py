import os
import sys
import socket
import pytest
from subprocess import Popen, TimeoutExpired
import time
from cashd.const import PORT, PROJECT_ROOT


@pytest.fixture(scope="session")
def local_ip():
    """Fixture to programmatically find the local network IP (192.168.X.X)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        pytest.skip("No local network IP found.")
    finally:
        s.close()
    return ip


def is_server_running() -> bool:
    """Helper to check if Cashd is being served on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def start_server() -> Popen:
    """Starts the `cashd-server` in the background and return the started process.

    :raises TimeoutError: If the service takes too long to start.
    """
    # add env variables required by NiceGUI
    env = os.environ.copy()
    env["NICEGUI_SCREEN_TEST_PORT"] = str(PORT)
    process = Popen(
        [sys.executable, PROJECT_ROOT / "app.py"],
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=env,
    )
    timeout = 10
    start_time = time.time()
    while not is_server_running():
        if time.time() - start_time > timeout:
            process.terminate()
            raise TimeoutError(f"Server failed to start within {timeout=}s.")
        time.sleep(0.2)
    return process


@pytest.fixture(scope="session", autouse=True)
def ensure_nicegui_server():
    """Ensures NiceGUI is running before tests start and kills the server on teardown,
    but only if this fixture started it.
    """
    process = None
    if not is_server_running():
        process = start_server()
    yield
    if process is not None:
        process.terminate()
        try:
            process.wait(timeout=6)
        except TimeoutExpired:
            process.kill()  # Force kill if it's stubborn
