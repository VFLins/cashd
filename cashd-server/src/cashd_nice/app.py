
import multiprocessing
import sys

if sys.platform == 'linux':
    multiprocessing.set_start_method('spawn', force=True)

# NOTE: The above code must run before any app code. This avoids a possible Runtime Error:
# > A SemLock created in a fork context is being shared with a process in a spawn
# > context. This is not supported. Please use the same context to create
# > multiprocessing objects and Process.
# This is probably a bug in the current version of NiceGUI==3.11.1

import argparse
from pathlib import Path

from nicegui import ui, app
from cashd_nice.const import PROJECT_ROOT
from cashd_nice.pages import main, customer, stats, config


parser = argparse.ArgumentParser(
    prog="cashd-server", description="Execute o Cashd server, veja opções abaixo.",
    add_help=False
)
parser.add_argument("-h", "--help", action="help", help="Mostra esta mensagem de ajuda")
parser.add_argument(
    "-n", "--as-native", action="store_true",
    help=(
        "Execute o Cashd server localmente como um aplicativo nativo, outros "
        "dispositivos não poderão acessá-lo, e será executado em uma janela dedicada."
    )
)
args = parser.parse_args()

if hasattr(args, "help"):
    parser.print_help()
    quit()


app.add_static_files("/assets", Path(PROJECT_ROOT, "assets"))
app.native.window_args["min_size"] = (850, 650)


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


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Cashd server",
        show=False,
        native=args.as_native,
        favicon=PROJECT_ROOT / "assets/ICO_LogoIcone.ico",
    )

