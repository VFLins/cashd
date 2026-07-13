from .base import BaseSection
from sys import platform

from toga.app import App
from toga.style import Pack
from toga.widgets.box import Box, Row, Column
from toga.widgets.label import Label
from toga.widgets.table import Table
from toga.widgets.button import Button
from toga.widgets.switch import Switch
from toga.widgets.divider import Divider
from toga.widgets.selection import Selection
from toga.widgets.textinput import TextInput
from toga.widgets.numberinput import NumberInput
from toga.widgets.scrollcontainer import ScrollContainer
from toga.dialogs import (
    SelectFolderDialog,
    OpenFileDialog,
    InfoDialog,
    ErrorDialog,
)

from cashd_core import prefs, const
from cashd import style, backup, widgets
from cashd.widgets.elems import ListOfItems


class ConfigSection(BaseSection):
    def __init__(self, app: App):
        super().__init__(app)

        self.company_info = widgets.form.FormHandler(n_cols=1)
        self.company_info.add_fields(
            fields=[
                widgets.form.FormField(
                    label="Nome da empresa",
                    input_widget=TextInput(
                        value=prefs.CompanyName.get(),
                        on_change=lambda w: prefs.CompanyName.set(w.value),
                    ),
                ),
                widgets.form.FormField(
                    label="Local",
                    input_widget=TextInput(
                        value=prefs.CompanyAddress.get(),
                        on_change=lambda w: prefs.CompanyAddress.set(w.value),
                    ),
                ),
                widgets.form.FormField(
                    label="Info. de contato",
                    input_widget=TextInput(
                        value=prefs.CompanyContact.get(),
                        on_change=lambda w: prefs.CompanyContact.set(w.value),
                    ),
                ),
            ],
        )
        for field in self.company_info.fields.values():
            field.input.width = const.FORM_WIDTH

        self.default_values = widgets.form.FormHandler(n_cols=2)
        self.default_values.add_fields(
            fields=[
                widgets.form.FormField(
                    label="Estado",
                    input_widget=Selection(
                        items=const.ESTADOS,
                        value=prefs.settings.default_state,
                        on_change=self.set_default_state,
                    ),
                ),
                widgets.form.FormField(
                    label="Cidade",
                    input_widget=TextInput(
                        value=prefs.settings.default_city,
                        style=style.user_input(TextInput),
                        on_change=self.set_default_city,
                        on_lose_focus=self.set_title_case,
                    ),
                ),
                widgets.form.FormField(
                    label="Número de DDD",
                    input_widget=Selection(
                        items=const.DDD,
                        value=prefs.settings.area_code_number,
                        on_change=self.set_default_area_code,
                    ),
                ),
                widgets.form.FormField(
                    label="Linhas por página",
                    input_widget=NumberInput(
                        value=prefs.settings.data_tables_rows_per_page,
                        style=style.user_input(NumberInput),
                        on_change=self.set_rows_per_page,
                        max=500,
                        min=50,
                        step=10,
                    ),
                ),
            ]
        )

        self.backup_places_list = ListOfItems(
            datasource=backup.BackupPlacesSource(),
            columns=["value"],
            show_headings=False,
            on_add=self.add_backup_dir,
            on_rm=self.rm_backup_dir,
            label_text="Locais de backup",
            style=Pack(width=const.FORM_WIDTH),
        )

        self.transac_to_backup_amount = widgets.form.FormField(
            label="Qtd. de transações",
            input_widget=NumberInput(
                min=5,
                max=60,
                value=prefs.TransactionsPerBackup.get(),
                on_change=self.upd_transactions_per_backup,
            ),
            id="transac_to_backup_input",
        )
        self.transac_to_backup_amount_blank = Box(id="transac_to_backup_blank")
        self.backup_on_transac = Column(
            children=[
                Row(
                    style=Pack(align_items="center", margin_top=25),
                    children=[
                        Switch(
                            text="",
                            value=prefs.BackupOnTransaction.get(),
                            on_change=self.upd_backup_on_transaction,
                            style=Pack(
                                margin=(
                                    (0, 0, 0, 10)
                                    if platform == "win32"
                                    else (0, 10, 0, 0)
                                )
                            ),
                        ),
                        Label(
                            "Backup ao registrar transações",
                            style=Pack(font_size=const.FONT_SIZE),
                        ),
                    ],
                ),
            ],
        )
        self.backup_on_transac_container = Column(
            children=[
                self.backup_on_transac,
                (
                    self.transac_to_backup_amount
                    if prefs.BackupOnTransaction.get()
                    else self.transac_to_backup_amount_blank
                ),
                Label(
                    "Realiza um backup silenciosamente depois que uma quantidade "
                    "de\ntransações é registrada.",
                    style=style.input_annotation("legend"),
                ),
            ],
        )

        self.backup_on_close = Column(
            children=[
                Row(
                    style=Pack(align_items="center", margin_top=25),
                    children=[
                        Switch(
                            text="",
                            value=prefs.ForceBackupOnClose.get(),
                            on_change=lambda w: prefs.ForceBackupOnClose.set(w.value),
                            style=Pack(
                                margin=(
                                    (0, 0, 0, 10)
                                    if platform == "win32"
                                    else (0, 10, 0, 0)
                                )
                            ),
                        ),
                        Label(
                            "Forçar backup ao fechar",
                            style=Pack(font_size=const.FONT_SIZE),
                        ),
                    ],
                ),
                Label(
                    "Se desativado, isto só acontecerá se o banco de dados tiver "
                    "aumentado de\ntamanho desde o último backup.",
                    style=style.input_annotation("legend"),
                ),
            ],
        )

        self.backup_actions = widgets.form.FormHandler(n_cols=2)
        self.backup_actions.add_fields(
            fields=[
                widgets.form.FormField(
                    label="Ações",
                    input_widget=Button("Carregar backup", on_press=self.load_backup),
                    description="Esta operação é reversível, consulte\na documentação.",
                    id="load_backup_button",
                ),
                widgets.form.FormField(
                    label="",
                    input_widget=Button("Fazer backup", on_press=self.run_backup),
                    description="Backups serão salvos nos\n'Locais de backup'.",
                    id="run_backup_button",
                ),
            ],
        )

        self.company_info_section = Box(
            style=Pack(direction="column", width=const.CONTENT_WIDTH / 2),
            children=[
                Label("Informações da empresa", style=style.HEADING),
                Divider(style=style.SEPARATOR),
                self.company_info.widget,
            ],
        )

        self.default_values_section = Box(
            style=Pack(direction="column", width=const.CONTENT_WIDTH / 2),
            children=[
                Label("Valores padrão", style=style.HEADING),
                Divider(style=style.SEPARATOR),
                self.default_values.widget,
            ],
        )

        self.backup_section = Box(
            style=Pack(direction="column", width=const.CONTENT_WIDTH / 2),
            children=[
                Label("Backup", style=style.HEADING),
                Divider(style=style.SEPARATOR),
                self.backup_places_list.widget,
                self.backup_on_close,
                self.backup_on_transac_container,
                self.backup_actions.widget,
            ],
        )

        self.sections = Box(
            style=Pack(direction="column"),
            children=[
                self.company_info_section,
                self.default_values_section,
                self.backup_section,
            ],
        )
        self.main_container = Box(style=style.PAGE_BODY, children=[self.sections])
        self.full_contents = Box(
            style=style.FULL_CONTENTS, children=[self.main_container]
        )

    def upd_backup_on_transaction(self, widget: Switch):
        prefs.BackupOnTransaction.set(widget.value)
        input = self.transac_to_backup_amount
        blank = self.transac_to_backup_amount_blank
        if widget.value:
            self.backup_on_transac_container.replace(blank, input)
        else:
            self.backup_on_transac_container.replace(input, blank)

    def upd_transactions_per_backup(self, widget: NumberInput):
        value = int(widget.value)
        prefs.TransactionsPerBackup.set(value)
        prefs.TransactionsToBackup.set(value)

    def set_default_city(self, widget: TextInput):
        """Runs upon updating the 'Valores padrão: Cidade' field, writes the
        inserted city name to `prefs.conf`.
        """
        prefs.settings.default_city = widget.value
        print(f"Default city set to {prefs.settings.default_city}")

    def set_title_case(self, widget: TextInput):
        """Runs upon losing focus, set the text field value to title case."""
        value = widget.value.title()
        widget.value = value

    def set_default_state(self, widget: Selection):
        """Runs upon updating the 'Valores padrão: Estado' field, writes the
        inserted state acronym to `prefs.conf`.
        """
        prefs.settings.default_state = widget.value
        print(f"Default state set to {prefs.settings.default_state}")

    def set_default_area_code(self, widget: Selection):
        """Runs upon updating the 'Valores padrão: Número de DDD padrão' field,
        writes the selected number to `prefs.conf`.
        """
        prefs.settings.area_code_number = widget.value
        print(f"Default area code set to {prefs.settings.area_code_number}")

    def set_rows_per_page(self, widget: NumberInput):
        """Runs upon updating the 'Linhas por página' field, affects the number of rows
        in any paginated data widget.
        """
        prefs.settings.data_tables_rows_per_page = widget.value
        print(f"Amount of rows per page: {prefs.settings.data_tables_rows_per_page}")

    async def add_backup_dir(self, widget: Button):
        """Prompts the user to add a new directory where the backups will be stored."""
        dialog = SelectFolderDialog(title="Adicionar um local de backup")
        directory = await dialog._show(widget.window)
        if not directory:
            return
        backup.settings.add_backup_place(place=directory)
        print(f"Added backup place: {directory}")

    def rm_backup_dir(self, widget: Button):
        """Removes the selected item from the 'backup places' list."""
        selected_item = self.backup_places_list.selection
        if not selected_item:
            return
        idx = self.backup_places_list.data.index(selected_item)
        backup.settings.rm_backup_place(idx=idx)

    async def run_backup(self, widget: Button):
        """Performs a backup of the database to cashd's data dir and to the backup places."""
        backup_places = self.backup_places_list.data
        if len(backup_places) == 0:
            dialog = ErrorDialog(
                "Erro no backup de dados", "Nenhum local de backup adicionado."
            )
            dialog._show(window=widget.window)
        try:
            backup.run(force=True)
        except Exception as err:
            dialog = ErrorDialog(
                "Erro no backup de dados",
                f"Erro inesperado ao realizar backup:\n{err}.",
            )
            dialog._show(window=widget.window)
        else:
            dialog = InfoDialog(
                "Sucesso no backup de dados",
                f"Backup de dados realizado com sucesso para os locais de backup.",
            )
            dialog._show(window=widget.window)

    async def load_backup(self, widget: Button):
        """Prompts the user to select a backup file to be loaded as current database."""
        dialog = OpenFileDialog(
            "Escolha um arquivo de backup", file_types=["db", "sqlite"]
        )
        file_path = await dialog._show(window=widget.window)
        if not file_path:
            return
        backup.load(file=file_path)
