import multiprocessing
import sys
import os

if sys.platform == "linux":
    multiprocessing.set_start_method("spawn", force=True)

# NOTE: The above code must run before any app code. This avoids a possible Runtime Error:
# > A SemLock created in a fork context is being shared with a process in a spawn
# > context. This is not supported. Please use the same context to create
# > multiprocessing objects and Process.
# This is probably a bug in the current version of NiceGUI==3.11.1

import argparse
from pathlib import Path
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from nicegui import ui, app
from cashd_nice.const import PROJECT_ROOT
from cashd_nice.pages import main, customer, stats, config, login, user

parser = argparse.ArgumentParser(
    prog="cashd-server",
    description="Execute o Cashd server, veja opções abaixo.",
    add_help=False,
)
parser.add_argument("-h", "--help", action="help", help="Mostra esta mensagem de ajuda")
parser.add_argument(
    "-n",
    "--as-native",
    action="store_true",
    help=(
        "Execute o Cashd server localmente como um aplicativo nativo, outros "
        "dispositivos não poderão acessá-lo, e será executado em uma janela dedicada."
    ),
)
args = parser.parse_args()

if hasattr(args, "help"):
    parser.print_help()
    quit()


app.add_static_files("/assets", Path(PROJECT_ROOT, "assets"))
app.native.window_args["min_size"] = (850, 620)


@app.add_middleware
class AuthMiddleware(BaseHTTPMiddleware):
    HOST_IPS = ["127.0.0.1", "localhost"]
    UNRESTRICTED_ROUTES = {"/assets", "/login"}

    async def dispatch(self, request: Request, call_next):
        """Redirects to '/login' if the user is not authenticated, and to '/'
        if not authorized to access the requested page. The server's host bypasses
        any verification.
        """
        path = request.url.path
        if await self.is_host(request) or await self.is_safe_route(request):
            return await call_next(request)
        if not app.storage.user.get("authenticated", False):
            return RedirectResponse(f"/login")
        if not app.storage.user.get("authorized", False):
            return RedirectResponse("/")
        return await call_next(request)

    async def is_safe_route(self, request: Request) -> bool:
        """Check if the request's path is safe for anyone to access."""
        path = request.url.path
        is_from_module = path.startswith("/_nicegui")
        is_safe = path in self.UNRESTRICTED_ROUTES
        return is_safe or is_from_module

    async def is_host(self, request: Request) -> bool:
        """Check if the device accessing this GUI is the server's host."""
        client_host = request.client.host if request.client else None
        return client_host in self.HOST_IPS


@ui.page("/")
def main_page():
    return main.page(ui=ui)


@ui.page("/customer")
def customer_page():
    return customer.page(ui=ui)


@ui.page("/stats")
def stats_page():
    return stats.page(ui=ui)


@ui.page("/config")
def config_page():
    return config.page(ui=ui)


@ui.page("/login")
def login_page():
    if app.storage.user.get("authenticated"):
        return RedirectResponse("/")
    return login.page(ui=ui)


@ui.page("/user")
def user_page():
    return user.page(ui=ui)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Cashd server",
        show=False,
        native=args.as_native,
        storage_secret=os.urandom(16).hex(),
        favicon=PROJECT_ROOT / "assets/ICO_LogoIcone.ico",
    )
