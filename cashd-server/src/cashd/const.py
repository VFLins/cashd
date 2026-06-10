from pathlib import Path
import sys

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
