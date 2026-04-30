from pathlib import Path
from cashd_nice.const import PROJECT_ROOT
from nicegui import ui

header_entries = [
    ("Transações", "/transac"),
    ("Novo cliente", "/customer"),
    ("Estatísticas", "/stats"),
    ("Configurações", "/config"),
]

class DefaultHeader:
    def __init__(self, ui, selected_entry: int):
        with ui.header(elevated=True).style("background-color: #cadfe7"):
            ui.image(Path(PROJECT_ROOT, "/assets/cashd-logo.svg"))
            ui.label("Cashd").style("font-family: Saira")
            ui.space()
            for i, entry in enumerate(header_entries):
                if i == selected_entry:
                    ui.button(entry[0]).props("unelevated")
                else:
                    ui.button(entry[0], on_click=lambda: ui.navigate.to(entry[1])).props("flat text-color=black")


class DetailedList:
    def __init__(self, ui, items, on_select=None):
        self.ui = ui
        self.items = items
        self.on_select = on_select
        self.selected_index = None
        self.item_elements = []

        with ui.scroll_area() \
            .classes("w-full border border-gray-300 rounded-borders") as scroll:
            scroll.style("min-height: 300px;")
            with self.ui.list().props("separator").classes("w-full p-0 m-0"):
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
            self.item_elements[self.selected_index].classes(remove='bg-blue-300')
        self.selected_index = index
        self.item_elements[index].classes('bg-blue-300')
        if self.on_select:
            self.on_select(self.items[index])

