from sys import platform

import toga
from toga.app import App
from toga.style import Pack
from toga.dialogs import (
    SelectFolderDialog,
    OpenFileDialog,
    InfoDialog,
    ErrorDialog,
)

from cashd_core import prefs, const
from cashd import backup, widget
from cashd.style.vars import (
    user_input,
    HEADING,
    FULL_CONTENTS,
    PAGE_BODY,
)
from cashd.pages.base import BaseSection
from cashd.style.compose import ComposedBox, mod


class ConfigSection(BaseSection):
    def __init__(self, app: App):
        super().__init__(app)

        self.company_info = widget.form.FormHandler(n_cols=1)
        self.company_info.add_fields(
            fields=[
                widget.form.FormField(
                    label="Nome da empresa",
                    input_widget=toga.TextInput(
                        value=prefs.CompanyName.get(),
                        on_change=lambda w: prefs.CompanyName.set(w.value),
                    ),
                ),
                widget.form.FormField(
                    label="Local",
                    input_widget=toga.TextInput(
                        value=prefs.CompanyAddress.get(),
                        on_change=lambda w: prefs.CompanyAddress.set(w.value),
                    ),
                ),
                widget.form.FormField(
                    label="Informação de contato",
                    input_widget=toga.TextInput(
                        value=prefs.CompanyContact.get(),
                        on_change=lambda w: prefs.CompanyContact.set(w.value),
                    ),
                ),
            ],
        )
        for field in self.company_info.fields.values():
            field.input.width = const.FORM_WIDTH - 5

        self.default_values = widget.form.FormHandler(n_cols=2)
        self.default_values.add_fields(
            fields=[
                widget.form.FormField(
                    label="Estado",
                    input_widget=toga.Selection(
                        items=const.ESTADOS,
                        value=prefs.settings.default_state,
                        on_change=self.set_default_state,
                    ),
                ),
                widget.form.FormField(
                    label="Cidade",
                    input_widget=toga.TextInput(
                        value=prefs.settings.default_city,
                        on_change=self.set_default_city,
                        on_lose_focus=self.set_title_case,
                    ),
                ),
                widget.form.FormField(
                    label="Número de DDD",
                    input_widget=toga.Selection(
                        items=const.DDD,
                        value=prefs.AreaCodeNumber.get(),
                        on_change=lambda w: prefs.AreaCodeNumber.set(w.value),
                    ),
                ),
                widget.form.FormField(
                    label="Linhas por página",
                    input_widget=toga.NumberInput(
                        value=prefs.settings.data_tables_rows_per_page,
                        on_change=self.set_rows_per_page,
                        max=500,
                        min=50,
                        step=10,
                    ),
                ),
            ]
        )

        self.backup_places_list = widget.elems.ListOfItems(
            datasource=backup.BackupPlacesSource(),
            columns=["value"],
            show_headings=False,
            on_add=self.add_backup_dir,
            on_rm=self.rm_backup_dir,
            label_text="Locais de backup",
            style=Pack(width=const.FORM_WIDTH),
        )

        self.transac_to_backup_amount = widget.form.FormField(
            label="Qtd. de transações",
            input_widget=toga.NumberInput(
                min=5,
                max=60,
                value=prefs.TransactionsPerBackup.get(),
                on_change=self.upd_transactions_per_backup,
            ),
            id="transac_to_backup_input",
        )
        self.backup_on_transac = widget.GroupBox(
            title="Backup ao registrar transações",
            on_change=self.upd_backup_on_transaction,
            style=Pack(
                font_size=10 if toga.backend == "toga_winforms" else 11,
                direction="column",
                width=const.FORM_WIDTH,
                margin_top=40 if toga.backend == "toga_winforms" else 15,
                margin_bottom=2,
            ),
            children=[
                toga.Column(
                    style=Pack(margin_top=25 if toga.backend == "toga_gtk" else 0),
                    children=[
                        self.transac_to_backup_amount,
                        toga.Label(
                            "Realiza um backup silenciosamente depois que uma "
                            "quantidade de\ntransações é registrada.",
                            style=Pack(margin=(6, 0, 10, 5), font_size=9, color="gray"),
                        ),
                    ],
                )
            ]
        )
        self.transac_to_backup_amount.input.readonly = not prefs.BackupOnTransaction.get()
        self.backup_on_transac.value = prefs.BackupOnTransaction.get()

        self.backup_on_close = toga.Column(
            children=[
                toga.Row(
                    style=Pack(align_items="center", margin_top=25),
                    children=[
                        widget.Checkbox(
                            text="Forçar backup ao fechar",
                            value=prefs.ForceBackupOnClose.get(),
                            on_change=lambda w: prefs.ForceBackupOnClose.set(w.value),
                            style=Pack(
                                margin=(
                                    (0, 0, 0, 10)
                                    if platform == "win32"
                                    else (0, 10, 0, 0)
                                ),
                                font_size=10,
                            ),
                        ),
                    ],
                ),
                toga.Label(
                    "Se desativado, isto só acontecerá se o banco de dados tiver "
                    "aumentado de\ntamanho desde o último backup.",
                    style=Pack(font_size=9, margin=(6, 0, 10, 5), color="gray")
                ),
            ],
        )

        self.backup_actions = widget.form.FormHandler(n_cols=2)
        self.backup_actions.add_fields(
            fields=[
                widget.form.FormField(
                    label="Ações",
                    input_widget=toga.Button("Carregar backup", on_press=self.load_backup),
                    description="Esta operação é reversível, consulte\na documentação.",
                    id="load_backup_button",
                ),
                widget.form.FormField(
                    label="",
                    input_widget=toga.Button("Fazer backup", on_press=self.run_backup),
                    description="Backups serão salvos nos\n'Locais de backup'.",
                    id="run_backup_button",
                ),
            ],
        )

        self.company_info_section = toga.Box(
            style=Pack(direction="column", width=const.FORM_WIDTH),
            children=[
                toga.Label("Informações da empresa", style=HEADING),
                toga.Divider(),
                self.company_info.widget,
            ],
        )

        self.default_values_section = toga.Box(
            style=Pack(direction="column", width=const.FORM_WIDTH),
            children=[
                toga.Label("Valores padrão", style=HEADING),
                toga.Divider(),
                self.default_values.widget,
            ],
        )

        self.backup_section = toga.Box(
            style=Pack(direction="column", width=const.FORM_WIDTH),
            children=[
                toga.Label("Backup", style=HEADING),
                toga.Divider(),
                self.backup_places_list.widget,
                self.backup_on_close,
                self.backup_on_transac,
                self.backup_actions.widget,
            ],
        )

        self.sections = ComposedBox(
            mod.STRETCH, mod.V, mod.CENTER_ACROSS,
            children=[
                self.company_info_section,
                self.default_values_section,
                self.backup_section,
            ],
        )
        self.full_contents = toga.ScrollContainer(content=self.sections)

    def upd_backup_on_transaction(self, widget: widget.GroupBox):
        prefs.BackupOnTransaction.set(widget.value)
        self.transac_to_backup_amount.input.readonly = not widget.value
        widget.refresh()

    def upd_transactions_per_backup(self, widget: toga.NumberInput):
        value = int(widget.value)
        prefs.TransactionsPerBackup.set(value)
        prefs.TransactionsToBackup.set(value)

    def set_default_city(self, widget: toga.TextInput):
        """Runs upon updating the 'Valores padrão: Cidade' field, writes the
        inserted city name to `prefs.conf`.
        """
        prefs.settings.default_city = widget.value
        print(f"Default city set to {prefs.settings.default_city}")

    def set_title_case(self, widget: toga.TextInput):
        """Runs upon losing focus, set the text field value to title case."""
        value = widget.value.title()
        widget.value = value

    def set_default_state(self, widget: toga.Selection):
        """Runs upon updating the 'Valores padrão: Estado' field, writes the
        inserted state acronym to `prefs.conf`.
        """
        prefs.settings.default_state = widget.value
        print(f"Default state set to {prefs.settings.default_state}")

    def set_default_area_code(self, widget: toga.Selection):
        """Runs upon updating the 'Valores padrão: Número de DDD padrão' field,
        writes the selected number to `prefs.conf`.
        """
        prefs.settings.area_code_number = widget.value
        print(f"Default area code set to {prefs.settings.area_code_number}")

    def set_rows_per_page(self, widget: toga.NumberInput):
        """Runs upon updating the 'Linhas por página' field, affects the number of rows
        in any paginated data widget.
        """
        prefs.settings.data_tables_rows_per_page = widget.value
        print(f"Amount of rows per page: {prefs.settings.data_tables_rows_per_page}")

    async def add_backup_dir(self, widget: toga.Button):
        """Prompts the user to add a new directory where the backups will be stored."""
        dialog = SelectFolderDialog(title="Adicionar um local de backup")
        directory = await dialog._show(widget.window)
        if not directory:
            return
        backup.settings.add_backup_place(place=directory)
        print(f"Added backup place: {directory}")

    def rm_backup_dir(self, widget: toga.Button):
        """Removes the selected item from the 'backup places' list."""
        selected_item = self.backup_places_list.selection
        if not selected_item:
            return
        idx = self.backup_places_list.data.index(selected_item)
        backup.settings.rm_backup_place(idx=idx)

    async def run_backup(self, widget: toga.Button):
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

    async def load_backup(self, widget: toga.Button):
        """Prompts the user to select a backup file to be loaded as current database."""
        dialog = OpenFileDialog(
            "Escolha um arquivo de backup", file_types=["db", "sqlite"]
        )
        file_path = await dialog._show(window=widget.window)
        if not file_path:
            return
        backup.load(file=file_path)
