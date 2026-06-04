from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
PORT = 4344
HOST_IPS = ["127.0.0.1", "localhost"]
UNRESTRICTED_ROUTES = {"/assets", "/login"}
ADMIN_ROUTES = {"/config", "/user"}
