from pathlib import Path
from typing import Any, override

class CustomDialog:
    """Base class for any custom dialog."""

    def __init__(self, ui):
        self.ui = ui
        with ui.dialog() as self.dialog, ui.card().classes("w-full"):
            self._render_content(ui)

    def _render_content(self, ui):
        """Use this function to render the dialog's content."""

    async def open(self) -> Any:
        """Called to display the dialog to the user"""
        self._initial_state()
        return await self.dialog

    def _initial_state(self):
        """Use this to set the initial state of the dialog."""

    async def cancel(self):
        """Called when the user leaves the dialog without committing the operation."""
        self.dialog.submit(None)
        self._cleanup()

    def _cleanup(self):
        """Use this to perform any necessary cleanup after the dialog is closed."""



class SelectDirDialog(CustomDialog):
    def __init__(
        self,
        ui,
        initial_dir: Path,
    ):
        self.INITIAL_DIR, self.selected_dir = initial_dir, initial_dir
        super().__init__(ui)

    def _render_content(self, ui):
        with ui.row() as top_block:
            top_block.classes("justify-between w-full")
            ui.button(
                "Voltar", icon="arrow_back", on_click=self.select_upper_dir
            ).props("flat")
            ui.button(
                icon="close", on_click=lambda: self.dialog.submit(None)
            ).props("flat")
        with ui.scroll_area().classes("w-full"):
            with ui.list().props("dense separator select-none") as self.dir_list:
                self.dir_list.classes("w-full")
                self.show_dir(self.INITIAL_DIR)
        with ui.row(align_items="center") as bottom_block:
            bottom_block.classes("w-full h-[1rem] no-wrap whitespace-nowrap")
            with ui.scroll_area() as selected_dir_block:
                selected_dir_block.classes("w-full h-6 no-margin-scroll")
                self.selected_dir_label = ui.label(str(self.selected_dir))
                self.selected_dir_label.classes("no-wrap font-mono font-bold")
                self.selected_dir_label.style("color: #478eff;")
            ui.button(
                icon="add",
                on_click=lambda: self.dialog.submit(self.selected_dir),
            )

    def _initial_state(self):
        self.selected_dir_label.set_text(str(self.INITIAL_DIR))
        self.show_dir(self.INITIAL_DIR)
        self.selected_dir = self.INITIAL_DIR

    @property
    def displayed_items(self) -> list[Path]:
        return [row.dirpath for row in self.selectables]

    def show_dir(self, directory: Path):
        self.dir_list.clear()
        try:
            # Transform into list to raise the permission error
            dirs = list(i for i in directory.iterdir() if i.is_dir())
        except PermissionError:
            self._render_message(
                "O sistema não permite exibir o conteúdo desta pasta.",
                icon="block",
                color="var(--q-negative)",
            )
        else:
            if len(dirs) == 0:
                self._render_message("Nenhuma pasta aqui.")
            else:
                self._render_dirs(rows=dirs)

    def _render_message(
        self, text: str, icon: str = "info", color: str = "var(--q-info)"
    ):
        ui = self.ui
        self.selectables = []  # Signals that nothing is being displayed currently
        with self.dir_list:
            with ui.item():
                with ui.item_section().props("avatar"):
                    ui.icon(icon).style(f"color: {color};")
                with ui.item_section():
                    label = ui.label(text)
                    label.style(f"color: {color}; font-style: italic;")

    def _render_dirs(self, rows: list[Path]):
        ui = self.ui
        self.selectables = []
        with self.dir_list:
            for selectable in rows:
                with ui.item() as list_item:
                    list_item.dirpath = selectable
                    self.selectables.append(list_item)
                    list_item.on_click(lambda s=selectable: self.click_dir(s))
                    with ui.item_section().props("avatar"):
                        ui.icon("folder").style("color: #478eff;")
                    with ui.item_section():
                        ui.label(selectable.name)

    def click_dir(self, directory: Path):
        if self.selected_dir == directory:
            # open the directory if clicked on a highlighted dir
            self.show_dir(directory)
        else:
            self._highlight_row(directory)
            self._unhighlight_row(self.selected_dir)
        self.selected_dir = directory
        self.selected_dir_label.set_text(str(directory))

    def _highlight_row(self, directory: Path):
        ui = self.ui
        idx = self.displayed_items.index(directory)
        with self.selectables[idx] as row:
            row.clear()
            row.style("background-color: #478eff; color: white;")
            with ui.item_section().props("avatar"):
                ui.icon("folder").style("color: white;")
            with ui.item_section():
                ui.label(directory.name).style("color: white;")

    def _unhighlight_row(self, directory: Path):
        ui = self.ui
        if self.selected_dir in self.displayed_items:
            idx = self.displayed_items.index(self.selected_dir)
            with self.selectables[idx] as row:
                row.clear()
                row.style("background-color: white; color: #478eff;")
                with ui.item_section().props("avatar"):
                    ui.icon("folder").style("color: #478eff;")
                with ui.item_section():
                    ui.label(self.selected_dir.name).style("color: black;")

    def select_upper_dir(self):
        cur, new = self.selected_dir, self.selected_dir.parent
        if cur in self.displayed_items:
            self._unhighlight_row(cur)
        else:
            self.show_dir(new)
        if cur == new:
            return
        self.selected_dir = new
        self.selected_dir_label.set_text(str(new))

