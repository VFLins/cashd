import argparse

from nicegui import ui
from cashd_nice.pages import main, customer, stats, config


parser = argparse.ArgumentParser(
    prog="cashd-server", description="Execute o Cashd server, veja opções abaixo."
)
parser.add_argument(
    "-n", "--as-native", action="store_true",
    help=(
        "Execute o Cashd server localmente como um aplicativo, outros dispositivos não "
        "poderão acessá-lo, e será executado em uma janela dedicada."
    )
)
args = parser.parse_args()

if hasattr(args, "help"):
    parser.print_help()
    quit()


@ui.page("/")
def main_page():
    return main.page(ui=ui)


if __name__ in ["__main__", "__mp_main__"]:
    ui.run(title="Cashd server", native=args.as_native)

