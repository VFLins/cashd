import sys
from copy import deepcopy
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Type, Iterable, Callable

from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets.base import Widget
from toga.widgets.numberinput import NumberInput
from toga.widgets.textinput import TextInput
from toga.widgets.selection import Selection
from toga.widgets.box import Box, Row, StyleT
from toga.widgets.label import Label

from cashd_core import data
from cashd import const
from cashd.style.compose import ComposedBox, COLUMNS, STRETCH
from cashd.style.vars import (
    input_annotation,
    user_input,
)
from cashd.widgets.elems import (
    LabeledSelection,
    LabeledNumberInput,
)


class FormField(Box):

    def __new__(
        self,
        label: str,
        input_widget: Widget,
        description: str | None = None,
        id: str | None = None,
        is_required: bool = False,
        default_width: bool = True,
    ):
        """Crete a form field with label, input and description (optional). Saves
        references for all widgets added to this field.

        - :label: A `toga.Label` positioned above the input that holds the input title;
        - :input: The `input_widget` provided, should be a Toga widget that accepts
          user input;
        - :description: An extra `toga.Label` positioned below the input with extra
          information about it, will only be present if `description` is provided.

        :param label: Text displayed as the input's label.
        :param input_widget: A `Widget` that can recieve user input.
        :param description: (Optional) Text displayed belou the input widget explaining
          it's usage.
        :param id: (Optional) A text used as ID
        :param is_required: A boolean indicator if this input needs to be filled. Used
          mainly by `FormHandler`.
        :param default_width: Boolean indicating if should use default width of the
          input field or to all available width.

        :returns: A modified `toga.Box` that includes custom children and properties.
        """
        label_widget = Label(
            text=label,
            id=f"{id}_label" if id else f"{label}_label",
            style=input_annotation("label", default_width),
        )
        input_widget.style = user_input(type(input_widget), default_width)

        self.contents = Box(
            id=id if id else label,
            style=Pack(direction="column"),
            children=[label_widget, input_widget],
        )
        if description:
            description_widget = Label(
                text=description,
                id=f"{id}_desc" if id else f"{label}_desc",
                style=input_annotation("legend"),
            )
            self.contents.add(description_widget)
            self.contents.description = description_widget

        self.contents.label = label_widget
        self.contents.input = input_widget
        self.contents.is_required = is_required
        return self.contents


class FormHandler:
    def __init__(
        self,
        n_cols: int = 1,
        on_change: Callable[[Widget], None] | None = None,
    ):
        """
        :param n_cols: Initial number of columns for the grid layout.
        :param on_change: Add `on_change` handler that applies to every *non-required*
          `FormField` added.
        """
        self.n_cols = n_cols
        self._on_change = on_change
        self._widget = ComposedBox(COLUMNS(self.n_cols))
        self._fields: Dict[str, FormField] = {}

    @property
    def widget(self) -> ComposedBox:
        return self._widget

    def add_table_fields(
        self,
        table: data.dec_base = data.tbl_clientes(),
        id: str | None = None,
        style: Pack | None = None,
    ):
        """Adds multiple fields into this FormHandler based on a declared table. Each column name
        will be handled as its `FormField.id`, and each form field can be fetched as
        `self.fields['colname']`.

        :param table: Declared table, child of `cashd.data.dec_base`.
        :param id: Base ID value to be passed to the fields.
        :param style: Common stylesheet to apply to the container.
        """
        children = get_form_fields(table=table, on_change=self._on_change)
        self.add_fields(fields=children, id=id, style=style)

    def add_fields(
        self, fields: List[FormField], id: str | None = None, style: Pack | None = None
    ):
        """Adds multiple `FormField` objects into this FormHandler.

        :param fields: List of `FormField` objects.
        :param id: Base ID value to be passed to the fields.
        :param style: Common stylesheet to apply to the container.
        """
        if style:
            for k, v in style.__dict__.items():
                if v is not None:
                    setattr(self._widget.style, k, v)

        self._widget.add(*fields)
        self._save_field_refs()

    def clear(self):
        """Removes every `FormField` of `self.widget` along with their references."""
        self._fields = {}
        self._widget.clear()
        self._widget._raw_children.clear()
        self._widget.rebuild()

    def required_fields_are_filled(self) -> bool:
        """Checks if every required field in this form is not empty. Return `True` if
        there are no required fields.
        """
        return all(
            field.input.value.strip() not in [None, ""]
            for field in self.fields.values()
            if getattr(field, "is_required", False)
        )

    def reshape(self, n_cols: int):
        """Rebuilds the form grid layout with the specified amount of columns."""
        self.n_cols = n_cols
        self._widget.set_modifiers(COLUMNS(n_cols))

    @property
    def data(self) -> Dict[str, str]:
        """Data currently typed by the user in the form."""
        return {wdg_id: field.input.value for wdg_id, field in self._fields.items()}

    def _save_field_refs(self):
        """Populates `self.fields` with the children provided. Must run at the end of
        every transforming action.
        """
        children = self._widget._raw_children
        label_names = unique_strings(lst=[ch.id for ch in children])
        self._fields = {lb: ch for lb, ch in zip(label_names, children)}

    @property
    def fields(self) -> Dict[str, FormField]:
        """Dictionary with each `FormField` element stored in this `FormHandler`."""
        return self._fields

    @property
    def on_change(self) -> Callable | None:
        """Handles `on_change` calls for every of its `FormField`."""
        on_change_calls = [field.input.on_change for field in self.fields.values()]
        fields_are_set = all(call is not None for call in on_change_calls)
        if fields_are_set and (len(on_change_calls) > 0):
            return on_change_calls[0]
        return None

    @on_change.setter
    def on_change(self, func: Callable[[Widget], None]):
        self._on_change = func
        for field in self._fields.values():
            field.input.on_change = func


class HorizontalDateForm:
    MONTHS = (
        "Janeiro",
        "Fevereiro",
        "Março",
        "Abril",
        "Maio",
        "Junho",
        "Julho",
        "Agosto",
        "Setembro",
        "Outubro",
        "Novembro",
        "Dezembro",
    )

    def __init__(self, value: date = date.today()):

        self.year_input = LabeledNumberInput(
            label_text="Ano",
            style=user_input(NumberInput),
            min=1,
            max=9999,
            value=value.year,
        )

        self.month_input = LabeledSelection(
            label_text="Mês",
            style=user_input(Selection),
            items=self.MONTHS,
            value=self.MONTHS[value.month - 1],
            on_change=self._update_allowed_day_values,
        )

        self.day_input = LabeledNumberInput(
            label_text="Dia",
            style=user_input(NumberInput),
            min=1,
            max=self._last_day_of_month(),
            value=value.day,
        )

        self.widget = Row(
            children=[
                self.day_input.widget,
                self.month_input.widget,
                self.year_input.widget,
            ],
        )

    @property
    def value(self):
        return date(
            int(self.year_input.value), self._month_number(), int(self.day_input.value)
        )

    @value.setter
    def value(self, value: date):
        self.day_input.value = value.day
        self.month_input.value = self.MONTHS[value.month - 1]
        self.year_input.value = value.year

    def _last_day_of_month(self) -> int:
        year, month = int(self.year_input.value), self._month_number()
        return int((date(year, month, 1) + relativedelta(day=31)).day)

    def _update_allowed_day_values(self, widget):
        max_day = self._last_day_of_month()
        if self.day_input.value > max_day:
            self.day_input.value = max_day
        self.day_input.max = max_day

    def _month_number(self) -> int:
        """Returns the month number 1-12 of the currently selected month."""
        month_name = self.month_input.value
        return int(self.MONTHS.index(month_name) + 1)


def unique_strings(lst: List[str]) -> List[str]:
    """Make every item in `lst` unique by appending a suffix."""
    seen = {}
    for i, item in enumerate(lst):
        if item in seen:
            count = seen[item]
            while f"{item}_{count}" in seen:
                count += 1
            new_item = f"{item}_{count}"
            lst[i] = new_item
            seen[new_item] = 1
            seen[item] += 1
        else:
            seen[item] = 1
    return lst


def build_form_field(
    table: data.dec_base,
    fieldname: str,
    on_change: Callable | None = None,
) -> FormField:
    """Builds a `FormField` for a table's field."""
    if table.types[fieldname] is data.RequiredStateAcronym:
        val = getattr(table, fieldname, "")
        widget = Selection(
            value=(val if val in const.ESTADOS else const.ESTADOS[0]),
            items=const.ESTADOS,
            on_change=on_change,
        )
    else:
        val = getattr(table, fieldname, "")
        widget = TextInput(value=val if val else "", on_change=on_change)

    return FormField(
        label=table.display_names[fieldname],
        input_widget=widget,
        id=fieldname,
        is_required=(table.types[fieldname] in data.REQUIRED_TYPES),
    )


def get_form_fields(
    table: data.dec_base,
    on_change: Callable | None = None,
) -> List[FormField]:
    fieldnames = table.display_names.keys()
    return [build_form_field(table, fieldname, on_change) for fieldname in fieldnames]
