from typing import Any
from nicegui import ui
from cashd_core.data import _DataSource


class DetailedList:
    def __init__(self, ui, datasource: _DataSource, keys: list[str], on_select=None):
        self.title_key, self.subtitle_key = keys[:2]
        self.SOURCE = datasource
        self.ui = ui
        self.on_select = on_select
        self.selected_item = None
        self.selected_data = None
        self.displayed_items = []
        self.displayed_data = []
        self.search_bar = ui.input(label="Pesquisa", on_change=self._change_search)
        self.search_bar.props("outlined dense").classes("w-full mt-4")
        self.selection = self._selection(ui)
        self.pagination = self._pagination(ui)

    @property
    def current_data(self) -> list[dict[str, Any]]:
        return [r._asdict() for r in self.SOURCE.current_data]

    @property
    def pagination_text(self) -> str:
        min_idx, max_idx = self.SOURCE.min_idx + 1, self.SOURCE.max_idx
        if self.SOURCE.nrows == 0:
            return "0 itens"
        return f"{self.SOURCE.nrows} itens, mostrando {min_idx} até {max_idx}"

    def _selection(self, ui):
        with ui.scroll_area() as scroll:
            scroll.classes(
                "w-full border border-gray-300 rounded-borders no-margin-scroll"
            )
            scroll.style("min-height: 260px; height: calc(100svh - 380px);")
            self._render_list_items()

    def _pagination(self, ui):
        with ui.scroll_area().classes("h-[2rem] no-margin-scroll w-full items-end"):
            with ui.row(align_items="center").classes("w-full no-wrap"):
                ui.space()
                self.pagination_label = ui.label(self.pagination_text)
                self.pagination_label.classes("select-none truncate")
                with ui.row().classes("gap-0 no-wrap"):
                    (
                        ui.button(icon="arrow_back", on_click=self._previous_page)
                        .classes("text-xs")
                        .props("flat")
                    )
                    (
                        ui.button(icon="arrow_forward", on_click=self._next_page)
                        .classes("text-xs")
                        .props("flat")
                    )

    @ui.refreshable
    def _render_list_items(self, no_callback: bool = False):
        """Refreshes the selection list to reflect the current state of the
        `DetailedList.SOURCE`.
        """
        # selection_list = getattr(self, "selection_list", self.ui.list())
        self.displayed_items = []
        self.displayed_data = []
        with self.ui.list() as selection_list:
            selection_list.props("separator dense")
            selection_list.classes("w-full p-0 m-0 select-none")
            for data in self.current_data:
                with self.ui.item() as item:
                    item.on("click", lambda d=data: self._select_item(d))
                    item.props("clickable")
                    self.displayed_data.append(data)
                    self.displayed_items.append(item)
                    with self.ui.item_section():
                        self.ui.item_label(data[self.title_key]).classes(
                            "font-medium mt-1"
                        )
                        self.ui.item_label(data[self.subtitle_key]).classes(
                            "text-xs mb-1"
                        )
        self._select_item(self.selected_data, no_callback)

    def _select_item(self, data: dict[str, Any], no_callback: bool = False):
        """Updates the highlighted item and updates DetailedList.selected and
        DetailedList.selected_index' values accordingly.
        """
        self.selected_data = data
        for row in self.displayed_items:
            row.style("background-color: white; color: black")
        if self.selected_data in self.displayed_data:
            idx = self.displayed_data.index(self.selected_data)
            item = self.displayed_items[idx]
            item.style("background-color: #478eff; color: white")
        if self.on_select and not no_callback:
            self.on_select(self.selected_data)

    def _next_page(self):
        """When available, renders the next page of data."""
        self.SOURCE.fetch_next_page()
        # self._render_list_items()
        self._render_list_items.refresh()
        self.pagination_label.text = self.pagination_text

    def _previous_page(self):
        """When available, renders the previous page of data."""
        self.SOURCE.fetch_previous_page()
        # self._render_list_items()
        self._render_list_items.refresh()
        self.pagination_label.text = self.pagination_text

    def _change_search(self):
        self.SOURCE.search_text = self.search_bar.value
        # self._render_list_items()
        self._render_list_items.refresh()
        self.pagination_label.text = self.pagination_text
