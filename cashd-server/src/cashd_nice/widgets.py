from nicegui import ui

header_entries = [
    ("/assets/SVG_TransacaoBranco.svg", "Transações", "/transac"),
    ("/assets/SVG_ContasBranco.svg", "Novo cliente", "/customer"),
    ("/assets/SVG_DadosBranco.svg", "Estatísticas", "/stats"),
    ("/assets/SVG_ConfiguracaoBranco.svg", "Configurações", "/config"),
]


class DefaultHeader:
    def __init__(self, ui, selected_entry: int):
        ui.add_css(
            """
            @font-face {
                font-family: 'Saira';
                src: url('/assets/Saira-Regular.ttf') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
            """
        )
        with ui.header(elevated=True).style("background-color: #cadfe7"):
            for i, entry in enumerate(header_entries):
                if i == selected_entry:
                    with ui.button().props("unelevated"):
                        ui.image(entry[0]).classes("rounded-full size-8 mr-3 mt-1 mb-1")
                        (
                            ui.label(entry[1])
                            .style("font-family: Saira; text-transform: none")
                        )
                else:
                    with (
                        ui.button(on_click=self.navigate_to(ui, entry[2]))
                        .props("flat")
                        .classes("m-0")
                    ) as btn:
                        ui.image(entry[0]).classes("rounded-full size-8 mr-3 mt-1 mb-1")
                        (
                            ui.label(entry[1]).style("color: black;")
                            .style("font-family: Saira; text-transform: none")
                        )

    def navigate_to(self, ui, url: str):
        return lambda: ui.navigate.to(url)


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

