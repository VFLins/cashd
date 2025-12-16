from typing import Type, Callable

from toga.style import Pack
from toga.widgets.base import Widget
from toga.widgets.table import Table
from toga.widgets.textinput import TextInput
from toga.widgets.detailedlist import DetailedList

from cashd_core import data
from cashd import style
from .elems import _DataInteractor


class PaginatedDetailedList(_DataInteractor):
    """Create a `PaginatedDetailedList.widget` with:

    - A search field `self.search_field`;
    - a `toga.DetailedList` widget as `self.data_widget`;
    - and pagination controls `self.bottom_controls`.
    """

    def __init__(
        self,
        datasource: Type[data._DataSource],
        id: str | None = None,
        style: Pack | None = None,
        on_select: Callable[[Widget], None] = None,
    ):
        """Create a `toga.DetailedList` with pagination and search.

        :type id: ``str`` | ``None``
        :param id: The ID for the widget.
        :type style: ``Pack`` | ``None``
        :param style: A style object. If no style is provided, a default style
            will be applied to the widget.
        :type kwargs: ``Any``
        :param kwargs: Keyword arguments passed to the equivalent `_LabeledInput.data_widget` widget.
        """
        super().__init__(datasource=datasource, id=id, style=style, on_select=on_select)

    def _set_data_widget(self, id=None, style=None, on_select=None):
        self.data_widget = DetailedList(id=id, style=style, on_select=on_select)

    def refresh(self, widget: TextInput | None = None):
        """Fetches data and updates `self.data_widget`. Requires a data source with at
        least three columns in order, where:

        1. :id: identifier of each row's piece of data
        2. :title: main information of each row in the widget
        3. :subtitle: secondary piece of information of each row in the widget.
        """
        self._datasource._fetch_metadata(search_text=self.search_field.value)
        self.data_widget.data = []
        # Grabbing items by index enables it to generalize the data source
        self.data_widget.data = (
            {"id": r[0], "title": r[1], "subtitle": r[2]}
            for r in self._datasource.current_data
        )
        self.update_page_label()

    @property
    def width(self):
        return self.widget.style.width

    @width.setter
    def width(self, val):
        self.widget.style.width = val
        self.top_controls.style.width = val
        self.bottom_controls.style.width = val
        self.data_widget.style.width = val-5
        self.search_field.style.width = val-5


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
        self.data_widget = Table(
            id=id + "_data_widget" if id else None,
            style=style,
            accessors=accessors,
            on_select=on_select,
            **kwargs,
        )
