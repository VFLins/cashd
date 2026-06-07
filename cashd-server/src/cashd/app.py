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
import asyncio
from multiprocessing import freeze_support
from pathlib import Path
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from nicegui import ui, app
from cashd import auth
from cashd.const import PROJECT_ROOT, PORT, ADMIN_ROUTES, UNRESTRICTED_ROUTES, HOST_IPS
from cashd.pages import main, customer, stats, config, login, user

MIN_WINDOW_SIZE = (450, 620) if sys.platform == "win32" else (450, 660)
app.add_static_files("/assets", Path(PROJECT_ROOT, "assets"))
app.native.window_args["min_size"] = MIN_WINDOW_SIZE


def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cashd-server",
        description="Execute o Cashd server, veja opções abaixo.",
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help", action="help", help="Mostra esta mensagem de ajuda"
    )
    parser.add_argument(
        "-n",
        "--as-native",
        action="store_true",
        help=(
            "Execute o Cashd server localmente como um aplicativo nativo, outros "
            "dispositivos não poderão acessá-lo, e será executado em uma janela dedicada."
        ),
    )
    return parser


@app.add_middleware
class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        """Redirects to '/login' if the user is not authenticated, and to '/'
        if not authorized to access the requested page. The server's host bypasses
        any verification.
        """
        path = request.url.path
        if await self.is_host(request) or await self.is_safe_route(request):
            return await call_next(request)
        if app.storage.user.get("userid", None):
            return await self.redirect_to_allowed(request, call_next)
        else:
            return RedirectResponse("/login")

    async def is_safe_route(self, request: Request) -> bool:
        """Check if the request's path is safe for anyone to access."""
        path = request.url.path
        is_from_module = path.startswith("/_nicegui")
        is_safe = any(path.startswith(r) for r in UNRESTRICTED_ROUTES)
        return is_safe or is_from_module

    async def is_host(self, request: Request) -> bool:
        """Check if the device accessing this GUI is the server's host."""
        client_host = request.client.host if request.client else None
        return client_host in HOST_IPS

    async def redirect_to_allowed(self, request: Request, call_next):
        """Send user to the requested page if allowed, or to an allowed page
        otherwise.
        """
        user, role = auth.User(), auth.Role()
        path = request.url.path
        user.read(row_id=app.storage.user["userid"])
        forbidden_routes = user.forbidden_pages() + list(ADMIN_ROUTES)
        if path not in forbidden_routes:
            return await call_next(path)
        elif "/" not in forbidden_routes:
            return RedirectResponse("/")
        else:
            return RedirectResponse("/login")


@ui.page("/")
def main_page():
    return main.page(ui=ui, app=app)


@ui.page("/customer")
def customer_page():
    return customer.page(ui=ui, app=app)


@ui.page("/stats")
def stats_page():
    return stats.page(ui=ui, app=app)


@ui.page("/config")
def config_page():
    return config.page(ui=ui, app=app)


@ui.page("/login")
def login_page():
    if app.storage.user.get("authenticated"):
        return RedirectResponse("/")
    return login.page(ui=ui, app=app)


@ui.page("/user")
def user_page():
    return user.page(ui=ui)


def run():
    freeze_support()
    parser = get_argparser()
    args, _ = parser.parse_known_args()
    if hasattr(args, "help"):
        parser.print_help()
        quit()
    try:
        ui.run(
            title="Cashd server",
            language="pt-BR",
            port=PORT,
            show=False,
            native=args.as_native,
            reload=False,
            storage_secret=os.urandom(16).hex(),
            favicon=PROJECT_ROOT / "assets" / "ICO_LogoIcone.ico",
        )
    except KeyboardInterrupt:
        print("\nInterrupção solicitada, encerrando servidor...")


if __name__ in {"__main__", "__mp_main__"}:
    run()
