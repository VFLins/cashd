import os
import sys
import asyncio
from pyshortcuts import make_shortcut
from pathlib import Path
from typing import Callable
from importlib.metadata import version
from cashd_core import backup
from cashd_core.prefs import settings
from cashd_core.const import ESTADOS, DDD
from cashd.const import EXECUTABLE_PATH, PYTHON_PATH, PROJECT_ROOT
from cashd.widgets.parts import DefaultHeader, notify_error, notify_success
from cashd.widgets.dialogs import SelectDirDialog, SelectFileDialog


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
    @property
    def data(self) -> list[dict[str, str]]:
        return [{"name": place} for place in backup.settings.read_backup_places()]

    def __init__(self, ui):
        self.ui = ui
        self.initial_dir: Path = Path("~").expanduser()

        self.table = (
            ui.table(
                columns=[
                    {"name": "name", "label": None, "field": "name", "align": "left"},
                    {"name": "action", "label": ""},
                ],
                rows=self.data,
            )
            .classes("w-100 md:w-full")
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
        new_dir = await self.dialog_add_directory.show()
        if not new_dir:
            return
        try:
            backup.settings.add_backup_place(new_dir)
        except Exception as err:
            notify_error(self.ui, "Erro ao adicionar local de backup, verifique o log")
            raise err
        self.table.rows = self.data

    def rm_dir(self, payload):
        row_index = payload.args
        try:
            backup.settings.rm_backup_place(idx=row_index)
        finally:
            self.table.rows = self.data


class page:
    def __init__(self, ui, app):
        self.ui = ui
        DefaultHeader(ui, app, selected_entry="Configurações")
        self.file_dialog = SelectFileDialog(ui, initial_dir=Path("~").expanduser())
        with ui.column(align_items="left").classes("self-center"):

            h1(ui, "Preferências")
            h2(ui, "Valores padrão no formulário de contas")
            with ui.grid().classes("h-full center-items md:grid-cols-3"):
                self.state = ui.select(
                    ESTADOS,
                    value=settings.default_state,
                    label="Estado",
                    on_change=lambda: self.set_config("default_state", "state"),
                ).props("outlined dense")
                self.city = ui.input(
                    "Cidade",
                    value=settings.default_city,
                    on_change=lambda: self.set_config("default_city", "city"),
                ).props(
                    "outlined dense debounce=800"
                )  # debounce will delay the on_change call
                self.area_code = ui.select(
                    DDD,
                    value=settings.area_code_number,
                    label="Número do DDD",
                    on_change=lambda: self.set_config("area_code_number", "area_code"),
                ).props("outlined dense")
            h2(ui, "Linhas por página")
            with ui.grid().classes("h-full center-items md:grid-cols-3"):
                self.data_tables_rownumber = ui.number(
                    label="Tabelas de dados",
                    value=settings.data_tables_rows_per_page,
                    min=20,
                    max=500,
                    precision=0,
                    format="%.0f",
                    on_change=lambda: self.set_config(
                        "data_tables_rows_per_page", "data_tables_rownumber"
                    ),
                ).props("outlined dense debounce=800")
                self.data_tables_rownumber.classes("w-51")
                with self.data_tables_rownumber.add_slot("append"):
                    button = ui.button(
                        icon="refresh",
                        on_click=lambda: self.data_tables_rownumber.set_value(200),
                    )
                    button.props("flat dense")

            h1(ui, "Backup")
            h2(ui, "Locais de backup")
            self.backup_places = DirectoryList(ui)
            h2(ui, "Ações")
            with ui.grid().classes("md:grid-cols-2"):
                described_button(
                    ui,
                    label="Carregar backup",
                    description="Esta operação é reversível, consulte a documentação.",
                    icon="download",
                    on_click=self.restore_backup,
                )
                described_button(
                    ui,
                    label="Fazer backup",
                    description="Backups serão salvos nos 'Locais de backup'.",
                    icon="save",
                    on_click=self.run_backup,
                )

            h1(ui, "Sobre")
            h2(ui, "Software")
            version_data = [
                ("Cashd Server", version("cashd")),
                ("Cashd Core", version("cashd_core")),
                ("NiceGUI", version("nicegui")),
            ]
            with ui.row().classes("gap-10"):
                for data in version_data:
                    with ui.column().classes("gap-0"):
                        name = ui.label(data[0])
                        name.style("font-weight: bold;")
                        ui.label(data[1])
            h2(ui, "Sessão atual")
            with ui.list().props("border rounded dense separator"):
                for link in app.urls:
                    with ui.item():
                        with ui.item_section():
                            ui.link(link, link, new_tab=True)
            h2(ui, "Desenvolvedor")
            with ui.row():
                ui.image(
                    "https://avatars.githubusercontent.com/u/42384822?v=4"
                ).classes("size-14 rounded-lg")
                with ui.column().classes("gap-0"):
                    ui.label("Vitor Lins").classes("text-lg text-bold")
                    ui.link(
                        "Entre em contato", "https://vitorlins.com.br", new_tab=True
                    )

            h1(ui, "Criar atalho")
            with ui.row():
                ui.button(
                    "Para executar como aplicativo",
                    icon="computer",
                    on_click=self.native_mode_shortcut,
                ).props("flat")
                ui.button(
                    "Para executar como servidor",
                    icon="dns",
                    on_click=self.server_mode_shortcut,
                ).props("flat")

    def set_config(self, config_name: str, input_name: str):
        val: str | float = getattr(self, input_name).value
        try:
            setattr(settings, config_name, val)
        except TypeError:
            getattr(self, input_name).value = getattr(settings, config_name)
        except Exception as err:
            notify_error(self.ui, "Erro ao definir valor padrão, verifique os logs")
            raise err
        else:
            if type(val) is float:
                val = int(val)
            notify_success(self.ui, f"Valor padrão definido: {val}")

    def run_backup(self):
        try:
            backup.run(force=True, _raise=True)
        except Exception as err:
            notify_error(self.ui, "Erro ao realizar backup, verifique os logs")
            raise err
        else:
            notify_success(self.ui, "Backup realizado com sucesso")

    async def restore_backup(self):
        filepath = await self.file_dialog.show()
        if not filepath:
            return
        try:
            backup.load(file=filepath, _raise=True)
        except Exception as err:
            notify_error(self.ui, "Erro ao restaurar backup, verifique os logs")
            raise err

    def native_mode_shortcut(self):
        """Creates shortcuts to start Cashd Server in native mode."""
        try:
            make_shortcut(
                f"{EXECUTABLE_PATH} --as-native",
                name=r"Cashd Server app",
                description="Execute como um aplicativo sem servi-lo para a rede local",
                icon=str(PROJECT_ROOT / "assets" / "ICO_LogoIcone.ico"),
                terminal=False,
                executable="",
            )
        except Exception:
            notify_error(self.ui, "Algo deu errado ao criar atalho, verifique os logs")
        else:
            notify_success(self.ui, "Atalho criado com sucesso")

    def server_mode_shortcut(self):
        """Creates shortcuts to start Cashd Server in server mode."""
        try:
            make_shortcut(
                str(EXECUTABLE_PATH),
                name=r"Cashd Server",
                description="Inicie o serviço do Cashd Server",
                icon=str(PROJECT_ROOT / "assets" / "ICO_LogoIcone.ico"),
                terminal=True,
                executable="",
            )
        except Exception:
            notify_error(self.ui, "Algo deu errado ao criar atalho, verifique os logs")
        else:
            notify_success(self.ui, "Atalho criado com sucesso")
