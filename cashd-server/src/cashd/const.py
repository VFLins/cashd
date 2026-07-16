from datetime import datetime
from pathlib import Path
import sys
import base64
import mimetypes


PROJECT_ROOT = Path(__file__).resolve().parent
PORT = 4344
HOST_IPS = ["127.0.0.1", "localhost"]
UNRESTRICTED_ROUTES = {"/assets", "/login"}
ADMIN_ROUTES = {"/config", "/user"}
EXECUTABLE_DIR = Path(sys.executable).parent
PYTHON_PATH = (
    EXECUTABLE_DIR / "pythonw.exe"
    if sys.platform == "win32"
    else EXECUTABLE_DIR / "python"
)
EXECUTABLE_PATH = (
    EXECUTABLE_DIR / "cashd-server.exe"
    if sys.platform == "win32"
    else EXECUTABLE_DIR / "cashd-server"
)
DEAMON_PATH = (
    EXECUTABLE_DIR / "cashd-serverd.exe"
    if sys.platform == "win32"
    else EXECUTABLE_DIR / "cashd-serverd"
)


def now() -> str:
    """Returns the current date and time for logging as a String."""
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def get_client_ip(ui) -> str | None:
    """Retrieves the real client IP address, handling reverse proxies securely.

    :returns: A string containing the IP address, or None if it's not an UI accessor.
    """
    try:
        client = ui.context.client
        request = client.request

        headers = request.headers
        forwarded = headers.get("x-forwarded-for") or headers.get("x-real-ip")
        if forwarded:
            # IP is the first item in a comma-separated data String
            return forwarded.split(",")[0].strip()
        return client.ip
    except RuntimeError:
        # Raised if called outside of a NiceGUI client connection context
        # (e.g., in background tasks or startup/shutdown events)
        return None


def is_host(ui) -> bool:
    """Returns a boolean indicating if this client is accessing the UI from the
    host address.
    """
    ip = get_client_ip(ui)
    return ip in HOST_IPS


def safe_download(ui, filepath: str):
    """Sends a file to be downloaded by the client using base-64 encoding, this
    prevents the browser from blocking the transaction when it's not run over https.

    :param filepath: Path to the file that will be sent.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"{filepath} does not exist.")

    mime_type, _ = mimetypes.guess_type(filepath)
    if not mime_type:
        mime_type = "application/octet-stream"

    with open(path, "rb") as f:
        file_bytes = f.read()
    base64_data = base64.b64encode(file_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{base64_data}"
    ui.download(data_url, filename=path.name)
