from typing import Iterable, Callable
from decimal import Decimal
import asyncio

from toga.style import Pack
from toga.widgets.box import Box, Column
from toga.widgets.base import Widget
from toga.widgets.label import Label
from toga.widgets.table import Table
from toga.widgets.button import Button
from toga.widgets.selection import Selection, SourceT
from toga.widgets.textinput import TextInput
from toga.widgets.numberinput import NumberInput
from toga.widgets.detailedlist import DetailedList

from cashd.style import input_annotation
from cashd import data, const, style


class _LabeledInput:
    def __init__(
        self,
        label_text: str,
        id: str | None = None,
        style: Pack | None = None,
        **kwargs,
    ):
        """Base class for creating input fields with labels. Get the generated Box by
        accessing :ref::`_LabeledInput.widget`.

        :type label_text: ``str``
        :param label_text: Text displayed on the `toga.Label` widget. This widget
            can be accessed from `_LabeledInput.label`.
        :type id: ``str`` | ``None``
        :param id: The ID for the widget.
        :type style: ``Pack`` | ``None``
        :param style: A style object. If no style is provided, a default style
            will be applied to the widget.
        :type kwargs: ``Any``
        :param kwargs: Keyword arguments passed to the equivalent `_LabeledInput.input` widget.
        """
        self.label = Label(
            text=label_text, id=id + "_label" if id else None, style=input_annotation()
        )
        self._set_input(id=id + "_input" if id else None, style=style, **kwargs)
        self.widget = Column(id=id, style=style, children=[self.label, self.input])

    def _set_input(self, id, style, **kwargs):
        """Used by `_LabeledInput`'s children to define the input widget.

        :param id: Used by `self.__init__()` to define input widget's ID.
        :param kwargs: Arguments fowarded from `self.__init__()`to the input widget.
        """
        self.input = TextInput(id=id, style=style, **kwargs)

    @property
    def value(self) -> object:
        """Provides direct access to `self.input.value`, allowing this class to mimic
        it's behavior.
        """
        return self.input.value

    @value.setter
    def value(self, value: object):
        self.input.value = value

    @property
    def on_change(self) -> Callable:
        """Provides direct access to `self.input.on_change`, allowing this class to mimic
        it's behavior.
        """
        return self.input.on_change

    @on_change.setter
    def on_change(self, func: Callable):
        self.input.on_change = func


class LabeledNumberInput(_LabeledInput):
    def __init__(
        self,
        label_text: str,
        id: str | None = None,
        style: Pack | None = None,
        **kwargs,
    ):
        """Implementation of `toga.NumberInput` with a static label on top.

        :param label_text: Text displayed on the `toga.Label` widget.
        :param id: The ID for `self.widget`.
        :param kwargs: Arguments passed to :ref:`toga.NumberInput`.
        """
        super().__init__(label_text, id, style, **kwargs)

    def _set_input(self, id, style, **kwargs):
        self.input = NumberInput(id=id, style=style, **kwargs)

    @property
    def max(self) -> Decimal | None:
        """Provides direct access to `self.input.max`, allowing this class to mimic
        it's behavior.
        """
        return self.input.max

    @max.setter
    def max(self, value: Decimal):
        self.input.max = value

    @property
    def min(self) -> Decimal | None:
        """Provides direct access to `self.input.min`, allowing this class to mimic
        it's behavior.
        """
        return self.input.min

    @min.setter
    def min(self, value: Decimal):
        self.input.min = value

    @property
    def step(self) -> Decimal:
        """Provides direct access to `self.input.step`, allowing this class to mimic
        it's behavior.
        """
        return self.input.step

    @step.setter
    def step(self, value: Decimal):
        self.input.step = value


class LabeledSelection(_LabeledInput):
    def __init__(
        self,
        label_text: str,
        id: str | None = None,
        style: Pack | None = None,
        **kwargs,
    ):
        """Implementation of `toga.Selection` with a static label on top.

        :param label_text: Text displayed on the `toga.Label` widget.
        :param id: The ID for `self.widget`.
        :param kwargs: Arguments passed to :ref:`toga.Selection`.
        """
        super().__init__(label_text, id, style, **kwargs)

    def _set_input(self, id, style, **kwargs):
        self.input = Selection(id=id, style=style, **kwargs)

    @property
    def items(self):
        """Provides direct access to `self.input.items`, allowing this class to mimic
        it's behavior.
        """
        return self.input.items

    @items.setter
    def items(self, items: SourceT | Iterable | None):
        self.input.items = items


class _DataInteractor:
    def __init__(
        self,
        datasource: data._DataSource,
        label_text: str | None = None,
        id: str | None = None,
        style: Pack | None = None,
        on_select: Callable[[Widget], None] | None = None,
        **kwargs,
    ):
        """Base class for creating data widgets with other control widgets that interact
        with it's data. Get the generated Box by accessing :ref::`_LabeledInput.widget`.

        :type datasource: ``Type[cashd.db._DataSource]``
        :param datasource: A subclass of `cashd.db._DataSource`, that handles the data
          for the widget.
        :type label_text: ``str`` | ``None``
        :param label_text: Text displayed on the `toga.Label` widget. This widget
          can be accessed from `_LabeledInput.label`.
        :type id: ``str`` | ``None``
        :param id: The ID for the widget.
        :type style: ``Pack`` | ``None``
        :param style: A style object. If no style is provided, a default style
          will be applied to the widget.
        :type kwargs: ``Any``
        :param kwargs: Keyword arguments passed to the equivalent `_LabeledInput.data_widget` widget.
        """
        self._datasource = datasource

        if label_text:
            self.label = Label(
                text=label_text,
                id=id + "_label" if id else None,
                style=input_annotation(),
            )
        else:
            self.label = None

        self._set_data_widget(
            id=id + "_input" if id else None, style=style, on_select=on_select, **kwargs
        )
        self._set_top_controls()
        self._set_bottom_controls()

        widgets = [
            self.label,
            self.top_controls,
            self.data_widget,
            self.bottom_controls,
        ]
        # set widget = None if it shouldn't be included
        self.widget = Column(
            id=id,
            style=style,
            children=[w for w in widgets if w],
        )
        self.refresh()

    def _set_data_widget(
        self,
        id: str | None = None,
        style: Pack | None = None,
        on_select: Callable[[Widget], None] | None = None,
        **kwargs,
    ):
        """Used by `_DataInteractor`'s children to define `self.data_widget`."""
        self.data_widget = Table(id=id, style=style, on_select=on_select, **kwargs)
        self.data_widget.data = self._datasource.current_data

    def _set_top_controls(self):
        """Used by `_DataInteractor`'s children to define the controls that should
        appear on top of the data widget.
        """
        self.search_field = TextInput(
            style=Pack(font_size=const.FONT_SIZE, width=const.CONTENT_WIDTH),
            placeholder="Pesquisa",
            on_change=self.refresh,
        )
        if self._datasource.is_searchable():
            self.top_controls = Box(children=[self.search_field])
        else:
            self.top_controls = None

    def _set_bottom_controls(self):
        """Used by `_DataInteractor`'s children to define the controls that should
        appear below the data widget.
        """
        self.page_label = Label(
            "", style=Pack(font_size=const.FONT_SIZE - 2, margin=(5, 5, 5, 0))
        )
        if self._datasource.is_paginated():
            self.bottom_controls = Box(
                style=style.ROW_OF_BUTTONS,
                children=[
                    self.page_label,
                    Button(
                        "Anterior",
                        on_press=self.previous_page,
                        style=style.SMALL_BUTTON,
                    ),
                    Button(
                        "Próximo", on_press=self.next_page, style=style.SMALL_BUTTON
                    ),
                ],
            )
            self.update_page_label()
        else:
            self.bottom_controls = None

    def refresh(self):
        """Fetches data and updates `self.data_widget`."""
        # fix winforms bug where the new data would not appear until the
        # widget is interacted with, by emptying it before assigning new data
        self.data_widget.data = []
        self.data_widget.data = self._datasource.current_data

    def update_page_label(self):
        """Updates the pagination information near the pagination controls."""
        self._datasource._fetch_metadata(self.search_field.value)
        self.page_label.text = (
            f"{self._datasource.nrows} itens, "
            f"mostrando de {self._datasource.min_idx + 1} "
            f"até {self._datasource.max_idx}"
        )

    def next_page(self, widget: Button):
        """Performs actions that replaces the displayed data from the current page to the
        next.
        """
        self._datasource.fetch_next_page()
        self.refresh()
        self.update_page_label()

    def previous_page(self, widget: Button):
        """Performs actions that replaces the displayed data from the current page to the
        previous.
        """
        self._datasource.fetch_previous_page()
        self.refresh()
        self.update_page_label()

    @property
    def data(self):
        """Provides direct access to `self.data_widget.data`, allowing this class to mimic
        it's behavior.
        """
        return self.data_widget.data

    @data.setter
    def data(self, value: Iterable):
        self.data_widget.data = value

    @property
    def selection(self):
        """Provides direct access to `self.data_widget.data`, allowing this class to mimic
        it's behavior.
        """
        return self.data_widget.selection


class ListOfItems(_DataInteractor):
    def __init__(
        self,
        datasource: Callable[[], Iterable[dict]] | None = None,
        on_add: Callable[[Widget], None] | None = None,
        on_rm: Callable[[Widget], None] | None = None,
        label_text: str | None = None,
        id: str | None = None,
        style: Pack | None = None,
        **kwargs,
    ):
        super().__init__(
            datasource=datasource, label_text=label_text, id=id, style=style, **kwargs
        )
        self._on_add = on_add
        self._on_rm = on_rm

    def _set_top_controls(self):
        self.top_controls = None

    def _set_bottom_controls(self):
        self.add_button = Button(
            "Adicionar", on_press=self.on_add, style=style.SMALL_BUTTON
        )
        self.rm_button = Button(
            "Remover", on_press=self.on_rm, style=style.SMALL_BUTTON
        )
        self.bottom_controls = Box(
            style=Pack(margin=(0, 5)), children=[self.rm_button, self.add_button]
        )

    async def on_add(self, widget):
        if asyncio.iscoroutinefunction(self._on_add):
            await self._on_add(widget)
        else:
            self._on_add(widget)
        self.refresh()

    async def on_rm(self, widget):
        if asyncio.iscoroutinefunction(self._on_rm):
            await self._on_rm(widget)
        else:
            self._on_rm(widget)
        self.refresh()


def form_options_container(children, alignment="end") -> Box:
    """
    Return a `toga.Box` containing elements that shoud be displayed under a form.

    :param children: Widgets that will be contained in this `toga.Box`, usually buttons.
    :param alignment: Horizontal alignment of elements.
    """
    inner_container = Box(style=style.ROW_OF_BUTTONS, children=children)
    outer_container = Box(
        style=Pack(direction="column", align_items=alignment, width=const.FORM_WIDTH),
        children=[inner_container],
    )
    return outer_container
