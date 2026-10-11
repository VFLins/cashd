from typing import Iterable, Callable
from decimal import Decimal
import asyncio

import toga
from toga.style import Pack

from cashd_core import data
from cashd import const
from cashd.style.vars import (
    ROW_OF_BUTTONS,
    SMALL_BUTTON,
)


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
            self.label = toga.Label(
                text=label_text,
                id=id + "_label" if id else None,
                style=Pack(margin=(20, 5, 9, 5)),
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
        self.widget = toga.Column(
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
        self.data_widget = toga.Table(id=id, style=style, on_select=on_select, **kwargs)
        self.data_widget.data = self._datasource.current_data

    def _set_top_controls(self):
        """Used by `_DataInteractor`'s children to define the controls that should
        appear on top of the data widget.
        """
        self.search_field = toga.TextInput(
            style=Pack(font_size=const.FONT_SIZE, flex=1),
            placeholder="Pesquisa",
            on_change=self.refresh,
        )
        if self._datasource.is_searchable():
            self.top_controls = toga.Box(children=[self.search_field])
        else:
            self.top_controls = None

    def _set_bottom_controls(self):
        """Used by `_DataInteractor`'s children to define the controls that should
        appear below the data widget.
        """
        self.page_label = toga.Label(
            "", style=Pack(font_size=const.FONT_SIZE - 2, margin=(5, 5, 5, 0))
        )
        if self._datasource.is_paginated():
            self.bottom_controls = toga.Box(
                style=ROW_OF_BUTTONS,
                children=[
                    self.page_label,
                    toga.Button(
                        "Anterior",
                        on_press=self.previous_page,
                        style=SMALL_BUTTON,
                    ),
                    toga.Button("Próximo", on_press=self.next_page, style=SMALL_BUTTON),
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

    def next_page(self, widget: toga.Button):
        """Performs actions that replaces the displayed data from the current page to the
        next.
        """
        self._datasource.fetch_next_page()
        self.refresh()
        self.update_page_label()

    def previous_page(self, widget: toga.Button):
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
        self.add_button = toga.Button("Adicionar", on_press=self.on_add, style=SMALL_BUTTON)
        self.rm_button = toga.Button("Remover", on_press=self.on_rm, style=SMALL_BUTTON)
        self.bottom_controls = toga.Box(
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


def form_options(buttons: list, alignment="end", width=const.FORM_WIDTH) -> Box:
    """
    Return a `toga.Box` containing elements that shoud be displayed under a form.

    :param children: Widgets that will be contained in this `toga.Box`, usually buttons.
    :param alignment: Horizontal alignment of elements.
    """
    inner_container = toga.Box(style=ROW_OF_BUTTONS, children=buttons)
    outer_container = toga.Box(
        style=Pack(direction="column", align_items=alignment, width=width),
        children=[inner_container],
    )
    return outer_container


class FormattedDateInput(toga.DateInput):
    """Subclasse de toga.DateInput para GTK que substitui o calendário fixo

    por um Gtk.MenuButton + Gtk.Popover compacto, delegando dinamicamente
    todas as chamadas nativas (métodos e atributos como minDate/maxDate)
    para o Gtk.Calendar interno.
    """

    def __init__(self, format_str="%d/%m/%Y", **kwargs):
        self._user_on_change = kwargs.get("on_change", None)
        kwargs["on_change"] = self._handle_on_change

        super().__init__(**kwargs)

        self.format_str = format_str
        self._is_gtk = toga.backend == "toga_gtk"

        if self._is_gtk:
            self._setup_gtk_polymorphic_button()

    def _setup_gtk_polymorphic_button(self):
        from gi.repository import Gtk

        impl = self._impl
        self._gtk_calendar = impl.native
        self._popover = Gtk.Popover()
        self._popover.add(self._gtk_calendar)

        # 3. Cria o MenuButton
        self._btn_popover = Gtk.MenuButton(
            label=self.value.strftime(self.format_str), popover=self._popover
        )
        self._btn_popover.show_all()

        # Inject interface
        self._btn_popover.interface = self

        calendar = self._gtk_calendar
        btn = self._btn_popover
        # Redirect common calendar calls from 'btn' to 'calendar'
        for attr in ["minDate", "maxDate", "min_date", "max_date", "get_date"]:
            if hasattr(calendar, attr):
                setattr(btn, attr, getattr(calendar, attr))

        # Sobrescreve o __getattr__ do botão individual para redirecionar leituras
        original_getattr = getattr(btn, "__getattr__", None)

        def custom_getattr(name):
            if hasattr(calendar, name):
                return getattr(calendar, name)
            if original_getattr:
                return original_getattr(name)
            raise AttributeError(
                f"'{type(btn).__name__}' object has no attribute '{name}'"
            )

        btn.__getattr__ = custom_getattr

        # 6. Atualiza o impl.native para renderizar o botão na interface
        impl.native = self._btn_popover

    def _handle_on_change(self, widget, **kwargs):
        # Atualiza o rótulo do botão com a nova data e fecha o Popover
        if self._is_gtk and hasattr(self, "_btn_popover"):
            self._btn_popover.set_label(self.value.strftime(self.format_str))
            if hasattr(self, "_popover"):
                self._popover.popdown()

        # Dispara o evento 'on_change' do usuário, caso tenha sido fornecido
        if self._user_on_change:
            self._user_on_change(widget, **kwargs)
