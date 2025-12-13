from toga.app import App
from toga.style.pack import Pack
from toga.widgets.base import Widget
from toga.widgets.box import Box
from toga.widgets.button import Button

from cashd_core import data
from .base import BaseSection
from cashd import const, style, widgets
from cashd.widgets.form import FormHandler


class CreateCustomerSection(BaseSection):

    def __init__(self, app: App):
        super().__init__(app)
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

    def rearrange_widgets(self):
        width, height = self.window_size
        form_width = self.customer_form.full_contents.style.width
        expected_width = 590 if width > 700 else 400
        if form_width == expected_width:
            return
        if (width > 700):
            self.customer_form.reshape(n_cols=3)
        else:
            self.customer_form.reshape(n_cols=2)
        self.full_contents.children[1].style.width = form_width
        self.full_contents.style.width = form_width
