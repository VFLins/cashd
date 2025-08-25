from datetime import date
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Type, Iterable, Callable

from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets.base import Widget
from toga.widgets.numberinput import NumberInput
from toga.widgets.textinput import TextInput
from toga.widgets.selection import Selection
from toga.widgets.box import Box, StyleT, Column
from toga.widgets.label import Label

from cashd import style, data, const
from cashd.widgets.elems import (
    LabeledSelection,
    LabeledNumberInput,
)


class FormField(Box):
    """A modified `toga.Box` that includes children and properties:

    - :label: A `toga.Label` positioned above the input that holds the input title;
    - :input: The `input_widget` provided, should be a Toga widget that accepts user input;
    - :description: An extra `toga.Label` positioned below the input with extra information
      about it, will only be present if `description` is provided.
    """

    def __new__(
        self,
        label: str,
        input_widget: Type[Widget],
        description: str | None = None,
        id: str | None = None,
        is_required: bool = False,
    ):
        label_widget = Label(
            text=label,
            id=f"{id}_label" if id else f"{label}_label",
            style=style.input_annotation(),
        )
        input_widget.style = style.user_input(type(input_widget))

        self.contents = Box(
            id=id if id else label,
            style=Pack(direction="column"),
            children=[label_widget, input_widget],
        )
        if description:
            description_widget = Label(
                text=description,
                id=f"{id}_desc" if id else f"{label}_desc",
                style=style.input_annotation("legend"),
            )
            self.contents.add(description_widget)
            self.contents.description = description_widget

        self.contents.label = label_widget
        self.contents.input = input_widget
        self.contents.is_required = is_required
        return self.contents


class FormRow(Box):
    def __init__(
        self,
        id: str | None = None,
        style: StyleT | None = None,
        children: Iterable[Widget] | None = None,
        **kwargs,
    ):
        if children:
            self._assert_children_amount(*children)
        if style:
            style.direction = ROW
        else:
            style = Pack(direction=ROW, width=const.FORM_WIDTH)
        super().__init__(id, style, children)

    def add(self, *children):
        self._assert_children_amount(*children)
        super().add(*children)

    def _assert_children_amount(self, *new_children: Widget | None):
        current_children = getattr(self, "_children", [])
        n_children = len(current_children) + len(new_children)
        assert (
            n_children < 3
        ), f"FormRow object can only hold up to 2 children, {n_children} given."


class FormHandler:
    def __init__(
        self,
        on_change: Callable[[Widget], None] | None = None,
        on_change_required: Callable[[Widget], None] | None = None,
    ):
        """
        :param on_change: Add `on_change` handler that applies to every *non-required*
          `FormField` added.
        :param on_change_required:  Add `on_change` handler that applies to every
          *required* `FormField` added.
        """
        self._on_change = on_change
        self._on_change_required = on_change_required
        self._full_contents = Box(
            style=Pack(
                direction=COLUMN, width=const.CONTENT_WIDTH, align_items="center"
            )
        )

    @property
    def full_contents(self):
        return self._full_contents

    def add_table_fields(
        self,
        table: data.dec_base = data.tbl_clientes(),
        id: str | None = None,
        style: Pack | None = None,
    ):
        """Adds multiple `cashd.widgets.form.FormRow` into this FormHandler. Each item in
        children is added in pairs to the form rows.

        :param table: Declared table, child of `cashd.data.dec_base`. Each column name
          will be handled as it's `FormField.id`, and each form field can be fetched as
          `self.fields['colname']`.
        :param id: Base ID value to be passed to the rows, a number will. If not empty,
          be appended to the end indicating the row number.
        :param style: Common stylesheet for all rows.
        """
        children = get_form_fields(
            table=table,
            on_change=self._on_change,
            on_change_required=self._on_change_required,
        )
        self.add_fields(fields=children, id=id, style=style)

    def add_fields(
        self, fields: List[FormField], id: str | None = None, style: Pack | None = None
    ):
        """Adds muiltiple `cashd.widgets.form.FormRow` into this FormHandler

        :param fields: List of `FormRow` objects.
        :param id: Base ID value to be passed to the rows, a number will. If not empty,
          be appended to the end indicating the row number.
        :param style: Common stylesheet for all rows.
        """
        n_rows = int(len(fields) / 2 + 0.5)
        for rn in range(n_rows):
            min_idx = rn * 2
            max_idx = min_idx + 2
            children_subset = [c for c in fields[min_idx:max_idx]]
            row = FormRow(children=children_subset, id=id, style=style)
            self._full_contents.add(row)
        self._save_field_refs()

    def clear(self):
        """Removes every FormRow of `self.full_contents` along with their `FormField`'s
        references.
        """
        self._fields = {}
        self._full_contents.clear()

    def required_fields_are_filled(self) -> bool:
        """Checks if every required field in this form is not empty. Return `True` if
        there are no required fields.
        """
        return all(
            form_field.children[1].value.strip()
            not in [None, ""]  # input widget at [1]
            for row in self.full_contents.children
            for form_field in row.children
            if form_field.is_required
        )

    @property
    def data(self) -> Dict[str, str]:
        """Data currently typed by the user in the form."""
        return {wdg_id: self._fields[wdg_id].input.value for wdg_id in self._fields}

    def _save_field_refs(self):
        """Populates `self.fields` with the children provided. Must be run at the end of
        every transforming action.
        """
        children = [
            field for row in self.full_contents.children for field in row.children
        ]
        label_names = unique_strings(lst=[ch.id for ch in children])
        self._fields = {lb: ch for lb, ch in zip(label_names, children)}

    @property
    def fields(self) -> Dict[str, FormField]:
        """Dictionary with each `FormField` element stored in this `FormHandler`."""
        return getattr(self, "_fields", {})

    @property
    def on_change_required(self):
        """Handles `on_change` calls for every of it's *required* `FormField`."""
        for field in self.fields.values():
            if field.is_reqired:
                return field.input.on_change

    @on_change_required.setter
    def on_change_required(self, func: Callable[[Widget], None]):
        for field in self.fields.values():
            if field.is_required:
                field.input.on_change = func

    @property
    def on_change(self) -> Callable | None:
        """Handles `on_change` calls for every of it's *non-required* `FormField`."""
        on_change_calls = [
            field.input.on_change
            for field in self.fields.values()
            if not field.is_required
        ]
        if all(on_change_calls) and (len(on_change_calls) > 0):
            return on_change_calls[0]
        else:
            return None

    @on_change.setter
    def on_change(self, func: Callable[[Widget], None]):
        for field in self._fields.values():
            if not field.is_required():
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
            style=style.user_input(NumberInput),
            min=1,
            max=9999,
            value=value.year,
        )

        self.month_input = LabeledSelection(
            label_text="Mês",
            style=style.user_input(Selection),
            items=self.MONTHS,
            value=self.MONTHS[value.month - 1],
            on_change=self._update_allowed_day_values,
        )

        self.day_input = LabeledNumberInput(
            label_text="Dia",
            style=style.user_input(NumberInput),
            min=1,
            max=self._last_day_of_month(),
            value=value.day,
        )

        self.full_contents = Box(
            style=style.DATE_INPUT_CONTROLS,
            children=[
                self.day_input.widget,
                self.month_input.widget,
                self.year_input.widget,
            ],
        )

    @property
    def value(self):
        return date(
            int(self.year_input.value), self._month_number(), int(
                self.day_input.value)
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
    on_change_required: Callable | None = None,
) -> List[FormField]:
    fields = []
    for fieldname in table.display_names.keys():
        if table.types[fieldname] in data.REQUIRED_TYPES:
            call = on_change_required
        else:
            call = on_change
        widget = build_form_field(table, fieldname, call)
        fields.append(widget)
    return fields
