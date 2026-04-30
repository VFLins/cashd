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


@ui.page("/")
def main_page():
    return main.page(ui=ui)


if __name__ in ["__main__", "__mp_main__"]:
    ui.run(title="Cashd server", native=args.as_native)

