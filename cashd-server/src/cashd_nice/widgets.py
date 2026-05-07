import platform
from pathlib import Path
from typing import Callable, Any

from nicegui import ui, events

header_entries = [
    ("/assets/SVG_TransacaoBranco.svg", "Transações", "/"),
    ("/assets/SVG_ContasBranco.svg", "Novo cliente", "/customer"),
    ("/assets/SVG_DadosBranco.svg", "Estatísticas", "/stats"),
    ("/assets/SVG_ConfiguracaoBranco.svg", "Configurações", "/config"),
]


class DefaultHeader:
    def __init__(self, ui, selected_entry: int):
        ui.add_css(
            """
            @font-face {
                font-family: 'Saira Semibold';
                src: url('/assets/Saira-SemiBold.ttf') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
            """
        )
        with ui.header(elevated=True) as header:
            header.style("background-color: #cadfe7")
            header.classes("gap-0")
            with ui.row() as default_block:
                default_block.classes("!hidden md:!flex w-full")
                for i, entry in enumerate(header_entries):
                    if i == selected_entry:
                        with ui.button().props("unelevated"):
                            btn_image = ui.image(entry[0])
                            btn_image.classes("rounded-full size-8 mr-3 mt-1 mb-1")
                            btn_label = ui.label(entry[1])
                            btn_label.classes("text-base")
                            btn_label.style(
                                "font-family: 'Saira Semibold'; "
                                "text-transform: none"
                            )
                    else:
                        with ui.button() as enabled_button:
                            enabled_button.on("click", self.navigate_to(ui, entry[2]))
                            enabled_button.props("flat")
                            btn_image = ui.image(entry[0])
                            btn_image.classes("rounded-full size-8 mr-3 mt-1 mb-1")
                            btn_label = ui.label(entry[1])
                            btn_label.classes("text-base")
                            btn_label.style(
                                "font-family: 'Saira Semibold'; "
                                "text-transform: none; "
                                "color: black;"
                            )
            with ui.row(align_items="center") as mobile_block:
                mobile_block.classes("sm:hidden w-full flex-nowrap")
                header_image = ui.image(header_entries[selected_entry][0])
                header_image.classes("rounded-full size-12 select-none")
                header_label = ui.label(header_entries[selected_entry][1])
                header_label.classes("text-2xl select-none truncate")
                header_label.style(
                    "font-family: 'Saira Semibold'; "
                    "text-transform: none; "
                    "color: #478eff;"
                )
                ui.space()
                with ui.button(icon="menu"):
                    with ui.menu() as menu:
                        for i, entry in enumerate(header_entries):
                            if i == selected_entry:
                                continue
                            with ui.menu_item(on_click=self.navigate_to(ui, entry[2])):
                                with ui.row().classes("items-center gap-2 no-wrap"):
                                    ui.image(entry[0]).classes("rounded-full size-8 mr-3")
                                    ui.label(entry[1]).classes("whitespace-nowrap select-none")

    def navigate_to(self, ui, url: str):
        return lambda: ui.navigate.to(url)


class DetailedList:
    def __init__(self, ui, items, on_select=None):
        self.ui = ui
        self.items = items
        self.on_select = on_select
        self.selected_index = None
        self.item_elements = []

        with ui.scroll_area() as scroll:
            scroll.classes("w-full border border-gray-300 rounded-borders")
            scroll.style("min-height: 260px; height: calc(100svh - 460px);")
            with self.ui.list().props("separator").classes("w-full p-0 m-0 select-none"):
                for index, item in enumerate(self.items):
                    with self.ui.item(on_click=lambda i=index: self._select_item(i)).props('clickable v-ripple') as el:
                        self.item_elements.append(el)
                        with self.ui.item_section():
                            self.ui.item_label(item['title']).classes('text-weight-bold')
                            self.ui.item_label(item['subtitle'])

    def _select_item(self, index):
        """Updates the highlighted item and updates DetailedList.selected and
        DetailedList.selected_index' values accordingly.
        """
        if self.selected_index is not None:
            self.item_elements[self.selected_index].style("background-color: white; color: black")
        self.selected_index = index
        self.item_elements[index].style("background-color: #478eff; color: white")
        if self.on_select:
            self.on_select(self.items[index])


class SelectDirDialog:
    def __init__(
        self,
        ui,
        initial_dir: Path,
    ):
        self.ui = ui
        self.INITIAL_DIR, self.selected_dir = initial_dir, initial_dir
        with ui.dialog() as self.dir_selector, ui.card().classes("w-full"):
            with ui.row() as top_block:
                top_block.classes("justify-between w-full")
                ui.button(
                    "Voltar", icon="arrow_back", on_click=self.select_upper_dir
                ).props("flat")
                ui.button(
                    icon="close", on_click=lambda: self.dir_selector.submit(None)
                ).props("flat")
            with ui.scroll_area():
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
                    on_click=lambda: self.dir_selector.submit(self.selected_dir)
                )

    async def open(self) -> Path | None:
        self.selected_dir_label.set_text(str(self.INITIAL_DIR))
        self.show_dir(self.INITIAL_DIR)
        self.selected_dir = self.INITIAL_DIR
        return await self.dir_selector

    @property
    def displayed_items(self) -> list[Path]:
        return [row.dirpath for row in self.selectables]

    def show_dir(self, directory: Path):
        self.dir_list.clear()
        try:
            # NOTE: Transform into list to raise the permission error
            dirs = list(i for i in directory.iterdir() if i.is_dir())
        except PermissionError:
            self._render_message(
                "O sistema não permite exibir o conteúdo desta pasta.",
                icon="block",
                color="red",
            )
        else:
            if len(dirs) == 0:
                self._render_message("Nenhuma pasta aqui.")
            else:
                self._render_dirs(rows=dirs)

    def _render_message(self, text: str, icon: str = "info", color: str = "gray"):
        # INFO: Signals that nothing is being displayed currently
        self.selectables = []
        with self.dir_list:
            with ui.item():
                with ui.item_section().props("avatar"):
                    ui.icon(icon).style(f"color: {color};")
                with ui.item_section():
                    label = ui.label(text)
                    label.style(f"color: {color}; font-style: italic;")

    def _render_dirs(self, rows: list[Path]):
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
        ui = self.ui
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

    async def add_dir(self):
        result = await self.dir_selector
        if result:
            self.ui.notify(f"Diretório adicionado {result}")
        else:
            self.ui.notify(f"Nenhum diretório adicionado")
