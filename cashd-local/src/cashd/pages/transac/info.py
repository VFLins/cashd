from sqlalchemy import exc
from toga.style import Pack
from typing import Callable
import toga
import sys

from cashd_core import data
from cashd.widgets.form import FormHandler
from cashd.style.compose import ComposedBox, mod


class Subsection:
    def __init__(
        self,
        selected_customer: data.tbl_clientes,
        on_update: Callable[[], None] | None = None,
    ):
        self.SELECTED_CUSTOMER = selected_customer
        self.on_update = on_update

        self.form = FormHandler(
            n_cols=1,
            on_change=self.handle_confirm_permission,
        )
        """Multiple text input fields containing the current information of the
        selected customer.
        """

        self.undo_button = toga.Button(
            "Desfazer",
            enabled=False,
            on_press=self.undo_changes,
        )
        """Button to undo any changes made by the user on `customer_data_form_widgets`.
        Enabled only when any information is changed."""

        self.confirm_button = toga.Button(
            "Confirmar",
            enabled=False,
            on_press=self.confirm_changes,
        )
        """Button to write any changes made by the user on `customer_data_form_widgets`
        to the database. Enabled only when any information is changed."""

        self.options_container = ComposedBox(
            mod.H, mod.MARGIN(r=16, t=8, b=4), mod.GAP(8),
            children=[self.undo_button, self.confirm_button],
        )
        self.body = toga.ScrollContainer(
            style=Pack(flex=5),
            content=self.form.widget,
        )
        self.full_contents = ComposedBox(
            mod.V, mod.END_ACROSS,
            children=[self.body, self.options_container]
        )
        if sys.platform == "win32":
            self.full_contents.style.background_color = "#F9F9F9"
            self.form.widget.style.background_color = "#F9F9F9"

    def handle_confirm_permission(self, widget: toga.Widget):
        """App behaviour when the user interacts with any of the fields of
        `customer_data_form`.
        """
        if self.form.required_fields_are_filled():
            self.confirm_button.enabled = True
        else:
            self.confirm_button.enabled = False
        self.undo_button.enabled = True

    def undo_changes(self, widget: toga.Button):
        self.undo_button.enabled = False
        self.confirm_button.enabled = False
        self.form.clear()
        self.form.add_table_fields(self.SELECTED_CUSTOMER)

    def confirm_changes(self, widget: toga.Button):
        new_data = data.tbl_clientes(Id=self.SELECTED_CUSTOMER.Id, **self.form.data)
        self.SELECTED_CUSTOMER.fill(new_data)
        try:
            self.SELECTED_CUSTOMER.update()
            self.form.clear()
            self.form.add_table_fields(self.SELECTED_CUSTOMER)
            print(f"customer data updated to: {new_data}")
        except exc.StatementError as err:
            self.undo_changes(widget)
            print(f"Alteração proibida: {str(err.args[0])}")

