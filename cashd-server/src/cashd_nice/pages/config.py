from pathlib import Path
from cashd_core.const import ESTADOS
from cashd_nice.widgets import DefaultHeader


def h1(ui, title: str):
    ui.markdown(f"# {title}").style(
    ).classes("select-none")
    ui.separator().style("background-color: #478eff;")


def h2(ui, title: str):
    ui.markdown(f"## {title}").classes("font-bold").classes("select-none")


class DirectoryList:
    def __init__(self, ui):
        self.ui = ui
        self.SELECTED_DIR = Path("~").expanduser()

        self.table = ui.table(
            columns=[
                {"name": "name", 'label': None, "field": "name", "align": "left"},
                {"name": "action", "label": ""},
            ],
            rows=[{"id": i+1, "name": f"/caminho/para/pasta{i}"} for i in range(2)],
        ).classes('w-full').props("hide-header")

        with self.table.add_slot('top-right'):
            ui.button("Adicionar", icon="add", on_click=self.add_dir).props("flat")
        with self.table.add_slot("body-cell-action"):
            with self.table.cell("action"):
                del_button = ui.button(icon="delete").props("flat size=sm dense")
                del_button.on(
                    "click",
                    js_handler="() => emit(props.row.id)",
                    handler=lambda e: ui.notify(f"Excluindo local id={e.args}")
                )
        with ui.dialog() as self.dir_selector, ui.card().classes("w-full"):
            with ui.row().classes("justify-between w-full"):
                ui.button(
                    "Voltar",
                    icon="drive_folder_upload",
                    on_click=self.select_upper_dir
                ).props("flat")
                ui.button(
                    icon="cancel",
                    on_click=lambda: self.dir_selector.submit(None)
                ).props("flat")
            with ui.scroll_area():
                with ui.list().props("dense separator") as self.dir_list:
                    self.dir_list.classes("w-full")
                    self._show_dir(self.SELECTED_DIR)
            ui.button(
                icon="check",
                on_click=lambda: self.dir_selector.submit(self.SELECTED_DIR)
            )

    def _show_dir(self, directory: Path = Path("~").expanduser()):
        ui = self.ui
        self.dir_list.clear()
        self.selectables = []
        for selectable in directory.iterdir():
            if selectable.is_dir():
                with ui.item(on_click=lambda: self.click_dir(selectable)) as list_item:
                    self.selectables.append(list_item)
                    if selectable == self.SELECTED_DIR:
                        list_item.style("background-color: #478eff; color: white;")
                    with ui.item_section().props("avatar"):
                        ui.icon("folder").style("color: #478eff;")
                    with ui.item_section():
                        ui.label(selectable.name)
            else:
                with ui.item() as list_item:
                    self.selectables.append(list_item)
                    with ui.item_section().props("avatar"):
                        ui.icon("description").style("color: gray;")
                    with ui.item_section():
                        ui.label(selectable.name).style("color: gray;")

    def click_dir(self, directory: Path):
        if not directory.is_dir():
            return
        self.ui.notify(f"Diretório '{directory}' selecionado")
        if self.SELECTED_DIR == directory:
            ui.notify(f"Mostrando pasta: {directory}")
            self._show_dir(directory)
        else:
            sel_idx = list(self.SELECTED_DIR.iterdir()).index(directory)
            self.selectables[sel_idx].style("background-color: #478eff; color: white;")

    def select_upper_dir(self):
        pass

    async def add_dir(self):
        result = await self.dir_selector
        if result:
            self.ui.notify(f"Diretório adicionado {result}")
        else:
            self.ui.notify(f"Nenhum diretório adicionado")



def page(ui):
    ui.add_css(
    """
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
    """
    )
    ui.colors(primary="#478eff", secondary="#d3d7d9")
    DefaultHeader(ui, selected_entry=3)
    with ui.column(align_items="left").classes("self-center"):
        h1(ui, "Preferências")
        h2(ui, "Valores padrão no formulário de contas")
        with ui.grid().classes("h-full center-items sm:grid-cols-3"):
            ui.input("Estado")
            ui.input("Cidade")
            ui.select(ESTADOS, value=ESTADOS[0], label="Estado")
        h2(ui, "Linhas por página nas tabelas")
        with ui.grid().classes("h-full center-items sm:grid-cols-3"):
            ui.number(
                label="Clientes [100]", value=100, min=20, precision=0, format="%.0f"
            )
            ui.number(
                label="Estatísticas [200]", value=200, min=20, precision=0, format="%.0f"
            )
        h1(ui, "Backup")
        h2(ui, "Locais de backup")
        DirectoryList(ui)
        h2(ui, "Ações")


