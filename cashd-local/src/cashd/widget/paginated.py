from typing import Type, Callable
import warnings

import toga
from toga.style import Pack

from cashd_core import data
from cashd import style, const
from .elems import _DataInteractor


class PaginatedDetailedList(_DataInteractor):
    """Create a `PaginatedDetailedList.widget` with:

    - A search field `self.search_field`;
    - a `toga.DetailedList` widget as `self.data_widget`;
    - and pagination controls `self.bottom_controls`.
    """

    def __init__(
        self,
        datasource: data._DataSource,
        id: str | None = None,
        style: Pack | None = None,
        on_select: Callable[[toga.DetailedList], None] = None,
        on_search: Callable[None, None] = None,
    ):
        """Create a `toga.DetailedList` with pagination and search.

        :param id: The ID for the widget.
        :param style: A style object.
        :param on_select: Behavior when the user selects an entry.
        :param on_search: Behavor when the user interacts with the search bar.
        :param kwargs: Keyword arguments passed to the data widget.
        """
        super().__init__(
            datasource=datasource,
            id=id,
            style=style,
            on_select=on_select,
            on_search=on_search,
        )

    def _set_data_widget(self, id=None, style=None, on_select=None, **kwargs):
        self.data_widget = toga.DetailedList(id=id, style=style, on_select=on_select)

    def refresh(self, widget: toga.TextInput | None = None):
        """Fetches data and updates `self.data_widget`. Requires a data source with at
        least three columns, in order:

        1. :id: identifier of each row's piece of data
        2. :title: main information of each row in the widget
        3. :subtitle: secondary piece of information of each row in the widget.
        """
        self._datasource._fetch_metadata(search_text=self.search_field.value)
        self.data_widget.data = []
        # Grabbing items by index enables it to generalize the data source
        self.data_widget.data = (
            {"id": r[0], "icon": const.ICON_PERSON, "title": r[1], "subtitle": r[2]}
            for r in self._datasource.current_data
        )
        self.update_page_label()

    def clear_selection(self):
        """Ensures every row on this DetailedList is unselected."""
        current_backend = getattr(toga, "backend", None)
        match current_backend:
            case "toga_winforms":
                self.data_widget._impl._set_selection(-1)
            case "toga_gtk":
                self.data_widget._impl.native_detailedlist.unselect_all()
            case _:
                if current_backend is not None:
                    warnings.warn(
                        "Unselecting all rows for DetailedList is not implemented "
                        f"on {current_backend=}"
                    )

    @property
    def width(self):
        return self.widget.style.width

    @width.setter
    def width(self, val):
        self.widget.style.width = val
        self.top_controls.style.width = val
        self.search_field.style.width = val
        self.bottom_controls.style.width = val
        self.data_widget.style.width = val - 5
        self.search_field.style.width = val - 5


class PaginatedTable(_DataInteractor):
    def __init__(
        self,
        datasource: data._DataSource,
        id: str | None = None,
        style: Pack | None = None,
        **kwargs,
    ):
        super().__init__(
            datasource, label_text=None, id=id, style=style, on_select=None, **kwargs
        )

    def _set_data_widget(
        self, id=None, style=None, accessors=None, on_select=None, **kwargs
    ):
        self.data_widget = toga.Table(
            id=id + "_data_widget" if id else None,
            style=style,
            accessors=accessors,
            on_select=on_select,
            **kwargs,
        )
