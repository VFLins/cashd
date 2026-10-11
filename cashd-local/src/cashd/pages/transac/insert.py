from typing import Callable
from toga.style import Pack
import datetime as dt
import toga
import sys
import re

from cashd_core import data, fmt
from cashd import const, widget
from cashd.style.compose import ComposedBox, mod


class Subsection:
    FIELD_WIDTH = 190

    def __init__(
        self,
        selected_customer: data.tbl_clientes,
        on_insert: Callable[[], None] | None = None,
    ):
        self.SELECTED_CUSTOMER = selected_customer
        self.on_insert = on_insert

        self.date = widget.form.FormField(
            label="Data",
            input_widget=widget.DateInput(),
        )
        """Custom date input form from 'Inserir transação' context."""
        self.date.style.width = self.FIELD_WIDTH

        self.amount_label = toga.Label(
            "Valor: R$ 0,00",
            style=Pack(margin=(20, 5, 9, 5)),
        )
        """Label that dynamically displays the currency amount that will be
        inserted by the user.
        """

        self.amount_input = toga.TextInput(
            style=Pack(width=self.FIELD_WIDTH),
            placeholder="0,00",
            on_change=self.update_amount_label,
            on_confirm=self.insert_transaction,
        )
        """Text input that only allows integer and decimal numbers. Receives the
        currency amount of the transaction.
        """
        # This input shall be enabled after checking if there are any
        # customers registered
        self.amount_input.enabled = False

        self.confirm_button = toga.Button(
            "Inserir",
            enabled=False,
            on_press=self.insert_transaction,
            style=Pack(margin_top=25, width=100),
        )
        """Button to write the transaction with date and currency amount inserted
        by the user to the database.
        """

        self.full_contents = ComposedBox(
            mod.COLUMNS(1, mod.END_ACROSS, mod.WIDTH(self.FIELD_WIDTH)),
            mod.V, mod.CENTER_ACROSS,
            children=[
                self.date,
                self.amount_label,
                self.amount_input,
                self.confirm_button,
            ],
        )
        if sys.platform == "win32":
            self.full_contents.style.background_color = "#F9F9F9"

    def insert_transaction(self, widget: toga.Button):
        """Register transaction data to the database."""
        amount_input = fmt.StringToCurrency(user_input=self.amount_input.value)
        if not amount_input.is_valid():
            return
        transac_data = data.tbl_transacoes(
            IdCliente=self.SELECTED_CUSTOMER.Id,
            CarimboTempo=dt.datetime.now(),
            DataTransac=self.date.input.value,
            Valor=amount_input.value,
        )
        transac_data.write()
        self.confirm_button.enabled = False
        self.amount_input.value = ""
        if self.on_insert is not None:
            self.on_insert()

    def update_amount_label(self, widget):
        """Updates the `SubsectionAddTransac.amount_label` to reflect the amount
        typed by the user.
        """
        setattr(widget, "value", re.sub(r"[^\d,-]", "", widget.value))
        amount_input = fmt.StringToCurrency(user_input=widget.value)
        self.amount_label.text = f"Valor: R$ {amount_input.display_value}"
        if amount_input.is_valid():
            # Enables button if a valid customer is selected
            if self.SELECTED_CUSTOMER.required_fields_are_filled():
                self.confirm_button.enabled = True
        else:
            self.confirm_button.enabled = False

