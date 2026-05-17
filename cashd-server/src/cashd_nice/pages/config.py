from pathlib import Path
from typing import Callable
from cashd_core.const import ESTADOS
from cashd_nice.widgets import DefaultHeader, SelectDirDialog


def h1(ui, title: str):
    with ui.column().classes("gap-1 w-full"):
        ui.markdown(f"# {title}").style().classes("select-none")
        ui.separator().style("background-color: #478eff;")


def h2(ui, title: str):
    with ui.column().classes("gap-0 m-0 p-0 w-full"):
        ui.markdown(f"## {title}").classes("font-bold mt-4 mb-0").classes("select-none")


def described_button(
    ui,
    label: str,
    description: str,
    on_click: Callable[[], None] | None = None,
    icon: str | None = None,
):
    with ui.column().classes("w-full gap-1"):
        ui.button(label, icon=icon, on_click=on_click)
        ui.label(description).classes("text-xs mb-2")


class DirectoryList:
    def __init__(self, ui):
        self.ui = ui
        self.initial_dir: Path = Path("~").expanduser()

        self.table = (
            ui.table(
                columns=[
                    {"name": "name", "label": None, "field": "name", "align": "left"},
                    {"name": "action", "label": ""},
                ],
                rows=[{"name": f"/caminho/para/pasta{i}"} for i in range(2)],
            )
            .classes("w-full")
            .props("hide-header")
        )

        with self.table.add_slot("top-right"):
            ui.button("Adicionar", icon="add", on_click=self.add_dir).props("flat")
        with self.table.add_slot("body-cell-action"):
            with self.table.cell("action"):
                del_button = ui.button(icon="delete").props("flat size=sm dense")
                del_button.on(
                    "click",
                    js_handler="() => emit(props.rowIndex)",
                    handler=self.rm_dir,
                )
        self.dialog_add_directory = SelectDirDialog(ui=ui, initial_dir=self.initial_dir)

    async def add_dir(self):
        new_dir = await self.dialog_add_directory.open()
        if new_dir:
            self.ui.notify(f"Pasta adicionada: {new_dir}")

    def rm_dir(self, payload):
        row_index = payload.args
        self.ui.notify(f"Excluindo local {row_index=}")


def page(ui):
    ui.add_head_html("""
    <style>
        .no-margin-scroll .q-scrollarea__content {
            padding: 0 !important;
        }
    </style>
    """)
    ui.add_css("""
    .nicegui-markdown h1 {
        margin: 16px 0px 0px 0px;
        width: 100%;
        font-size: 20px;
        font-family: 'Saira Semibold';
        color: #478eff;
    }
    .nicegui-markdown h2 {
        margin: 8px 0px 0px 0px;
        margin: 0px;
        font-size: 16px;
        font-weight: bold;
    }
    """)
    ui.colors(primary="#478eff", secondary="#d3d7d9", warning="#d48731", info="#478eff")
    ui.query("body").style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")
    DefaultHeader(ui, selected_entry=3)
    with ui.column(align_items="left").classes("self-center"):
        h1(ui, "Preferências")
        h2(ui, "Valores padrão no formulário de contas")
        with ui.grid().classes("h-full center-items sm:grid-cols-3"):
            ui.input("Estado")
            ui.input("Cidade")
            ui.select(ESTADOS, value=ESTADOS[0], label="Estado")
        h2(ui, "Linhas por página")
        with ui.grid().classes("h-full center-items sm:grid-cols-3"):
            ui.number(
                label="Seleção de clientes [100]",
                value=100,
                min=20,
                precision=0,
                format="%.0f",
            )
            ui.number(
                label="Tabelas [200]", value=200, min=20, precision=0, format="%.0f"
            )
        h1(ui, "Backup")
        h2(ui, "Locais de backup")
        DirectoryList(ui)
        h2(ui, "Ações")
        with ui.grid().classes("sm:grid-cols-2"):
            described_button(
                ui,
                label="Carregar backup",
                description="Esta operação é reversível, consulte a documentação.",
                icon="download",
            )
            described_button(
                ui,
                label="Fazer backup",
                description="Backups serão salvos nos 'Locais de backup'.",
                icon="save",
            )
