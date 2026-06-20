import os
import sys
import asyncio
import argparse
import threading
import multiprocessing

if not sys.platform.startswith("linux"):
    import pystray
    from PIL import Image
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
sys_tray = None  # Use the system tray object name early


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


def get_tray(app):
    icon_path = Path(PROJECT_ROOT, "assets", "cashd-wb.ico")
    menu = pystray.Menu(pystray.MenuItem("Encerrar", lambda: app.shutdown()))
    return pystray.Icon(
        name="Cashd Server tray",
        icon=Image.open(icon_path),
        title="O serviço do Cashd está em execução",
        menu=menu,
    )


@app.on_startup
async def show_tray():
    """Display the system tray icon when starting Cashd Server."""
    if multiprocessing.current_process().name != "MainProcess":
        # This must only run on the main process to avoid duplicate tray icons
        return
    if sys.platform.startswith("linux"):
        # This is not supported on linux systems
        return
    global sys_tray
    sys_tray = get_tray(app)
    thread = threading.Thread(target=sys_tray.run, daemon=True)
    thread.start()


@app.on_shutdown
async def hide_tray():
    """Hide the system tray even when the service is ended outside the tray."""
    if multiprocessing.current_process().name != "MainProcess":
        return
    if sys.platform.startswith("linux"):
        return
    global sys_tray
    if sys_tray is not None:
        sys_tray.stop()


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
            favicon=PROJECT_ROOT / "assets" / "cashd-bw.ico",
        )
    except KeyboardInterrupt:
        print("\nInterrupção solicitada, encerrando servidor...")


if __name__ in {"__main__", "__mp_main__"}:
    run()
