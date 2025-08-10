from cashd import const, style, prefs, backup, widgets
from cashd.widgets.elems import ListOfItems
from .base import BaseSection

from toga.dialogs import (
    SelectFolderDialog,
    OpenFileDialog,
    InfoDialog,
    ErrorDialog,
)
from toga.style import Pack
from toga.widgets.box import Box
from toga.widgets.label import Label
from toga.widgets.table import Table
from toga.widgets.button import Button
from toga.widgets.divider import Divider
from toga.widgets.textinput import TextInput
from toga.widgets.selection import Selection
from toga.widgets.scrollcontainer import ScrollContainer


class ConfigSection(BaseSection):
    def __init__(self):
        self.default_values_section_title = Label(
            "Valores padrão",
            style=Pack(
                font_size=const.BIG_FONT_SIZE,
                font_weight="bold",
                width=const.CONTENT_WIDTH,
                padding=(20, 5, 5, 5),
            ),
        )
        self.default_values_section_widgets = widgets.form.FormHandler()
        self.default_values_section_widgets.add_fields(
            fields=[
                widgets.form.FormField(
                    label="Estado padrão",
                    input_widget=Selection(
                        items=const.ESTADOS,
                        value=prefs.settings.default_state,
                        on_change=self.set_default_state,
                    ),
                ),
                widgets.form.FormField(
                    label="Cidade padrão",
                    input_widget=TextInput(
                        value=prefs.settings.default_city,
                        style=style.user_input(TextInput),
                        on_change=self.set_default_city,
                        on_lose_focus=self.set_title_case,
                    ),
                ),
            ]
        )
        self.statistics_prefs_section_title = Label(
            "Backup",
            style=Pack(
                font_size=const.BIG_FONT_SIZE,
                font_weight="bold",
                width=const.CONTENT_WIDTH,
                padding=(20, 5, 5, 5),
            ),
        )
        self.backup_places_list = ListOfItems(
            datasource=backup.BackupPlacesSource(),
            accessors=["value"],
            on_add=self.add_backup_dir,
            on_rm=self.rm_backup_dir,
            label_text="Locais de backup",
            style=Pack(width=const.FORM_WIDTH),
        )
        self.backup_actions = widgets.form.FormHandler()
        self.backup_actions.add_fields(
            fields=[
                widgets.form.FormField(
                    label="Ações",
                    input_widget=Button("Carregar backup",
                                        on_press=self.load_backup),
                    description="Esta operação é reversível, consulte\na documentação.",
                    id="load_backup_button",
                ),
                widgets.form.FormField(
                    label="",
                    input_widget=Button(
                        "Fazer backup", on_press=self.run_backup),
                    description="Backups serão salvos nos\n'Locais de backup'.",
                    id="run_backup_button",
                ),
            ],
        )

        self.first_section_content = Box(
            style=Pack(direction="column", width=const.CONTENT_WIDTH / 2),
            children=[
                self.default_values_section_title,
                Divider(style=style.SEPARATOR),
                self.default_values_section_widgets.full_contents,
            ],
        )

        self.second_section_content = Box(
            style=Pack(
                direction="column", width=const.CONTENT_WIDTH / 2, align_items="center"
            ),
            children=[
                self.statistics_prefs_section_title,
                Divider(style=style.SEPARATOR),
                self.backup_places_list.widget,
                self.backup_actions.full_contents,
            ],
        )

        self.option_sections = Box(
            style=Pack(direction="column"),
            children=[
                self.first_section_content,
                self.second_section_content,
            ],
        )
        self.forms = ScrollContainer(
            style=style.PAGE_BODY, content=self.option_sections
        )
        self.full_contents = Box(
            style=style.FULL_CONTENTS,
            children=[self.forms],
        )

    def set_default_city(self, widget: TextInput):
        """Runs upon updating the 'Cidade padrão' field, writes the inserted
        city name to `prefs.conf`.
        """
        prefs.settings.default_city = widget.value
        print(f"Default city set to {prefs.settings.default_city}")

    def set_title_case(self, widget: TextInput):
        """Runs upon losing focus, set the text field value to title case."""
        value = widget.value.title()
        widget.value = value

    def set_default_state(self, widget: Selection):
        """Runs upon updating the 'Estado padrão' field, writes the inserted
        state acronym to `prefs.conf`.
        """
        prefs.settings.default_state = widget.value
        print(f"Default state set to {prefs.settings.default_state}")

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
