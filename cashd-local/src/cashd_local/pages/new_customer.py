from toga.style.pack import Pack
from toga.widgets.base import Widget
from toga.widgets.box import Box
from toga.widgets.button import Button

from cashd.widgets.form import FormHandler
from .base import BaseSection
from cashd import const, style, data, widgets


class CreateCustomerSection(BaseSection):

    def __init__(self):
        # Winforms erroes if this class is instantiated outside a class function
        self.customer_form = FormHandler(
            on_change=self.change_not_required_fields,
            on_change_required=self.change_required_fields,
        )
        self.customer_form.add_table_fields(table=data.get_default_customer())
        self.undo_button = Button(
            "Desfazer",
            enabled=False,
            on_press=self.undo_changes,
            style=style.CONTEXT_BUTTON,
        )
        self.confirm_button = Button(
            "Confirmar",
            enabled=False,
            on_press=self.confirm_changes,
            style=style.CONTEXT_BUTTON,
        )
        self.controls = Box(
            style=style.ROW_OF_BUTTONS,
            children=[
                self.undo_button,
                self.confirm_button,
            ],
        )
        self.full_contents = Box(
            style=style.FULL_CONTENTS,
            children=[
                self.customer_form.full_contents,
                widgets.elems.form_options_container(
                    children=[self.undo_button, self.confirm_button]
                ),
            ],
        )

    def disable_buttons(self, widget: Widget):
        self.undo_button.enabled = True
        self.confirm_button.enabled = True

    def undo_changes(self, widget: Button):
        self.undo_button.enabled = False
        self.confirm_button.enabled = False
        self.update_data_widgets()

    def confirm_changes(self, widget: Widget):
        new_data = self.customer_form.data
        customer = data.tbl_clientes(**new_data)
        try:
            customer.write()
            print(f"Novo cliente adicionado: {new_data}")
        except ValueError as err:
            print(err)
        self.update_data_widgets()
        self.disable_buttons(widget=widget)

    def change_required_fields(self, widget: Widget):
        if self.customer_form.required_fields_are_filled():
            self.confirm_button.enabled = True
        else:
            self.confirm_button.enabled = False
        self.change_not_required_fields(widget)

    def change_not_required_fields(self, widget: Widget):
        self.undo_button.enabled = True

    def update_data_widgets(self):
        """Overrides inherited method, resets form to the default values."""
        self.customer_form.clear()
        self.customer_form.add_table_fields(table=data.get_default_customer())
