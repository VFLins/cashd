from nicegui import ui

class DetailedList:
    def __init__(self, items, on_select=None):
        self.items = items
        self.on_select = on_select
        self.selected_index = None
        self.item_elements = []

        # Container principal
        with ui.list().props('bordered separator').classes('w-full max-w-md'):
            for index, item in enumerate(self.items):
                # Cada item é um QItem (clicável)
                with ui.item(on_click=lambda i=index: self._select_item(i)).props('clickable v-ripple') as el:
                    self.item_elements.append(el)

                    with ui.item_section():
                        ui.item_label(item['title']).classes('text-weight-bold')
                        ui.item_label(item['subtitle'])

    def _select_item(self, index):
        # Remove o destaque do item anterior
        if self.selected_index is not None:
            self.item_elements[self.selected_index].classes(remove='bg-blue-100')

        # Aplica o destaque ao novo item
        self.selected_index = index
        self.item_elements[index].classes('bg-blue-100')

        # Dispara o callback, se existir
        if self.on_select:
            self.on_select(self.items[index])

