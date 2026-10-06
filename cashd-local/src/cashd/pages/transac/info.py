
class Subsection:
    def __init__(
        self,
        selected_customer: data.tbl_clientes,
        on_update: Callable[[], None] | None = None,
    ):
        self.SELECTED_CUSTOMER = selected_customer
        self.on_update = on_update

        self.form = widgets.form.FormHandler(
            n_cols=1,
            on_change=self.handle_confirm_permission,
        )
        """Multiple text input fields containing the current information of the
        selected customer.
        """

        self.undo_button = Button(
            "Desfazer",
            enabled=False,
            on_press=self.undo_changes,
            style=CONTEXT_BUTTON,
        )
        """Button to undo any changes made by the user on `customer_data_form_widgets`.
        Enabled only when any information is changed."""

        self.confirm_button = Button(
            "Confirmar",
            enabled=False,
            on_press=self.confirm_changes,
            style=CONTEXT_BUTTON,
        )
        """Button to write any changes made by the user on `customer_data_form_widgets`
        to the database. Enabled only when any information is changed."""

        self.options_container = get_container(
            H, MARGIN(r=15),
            children=[self.undo_button, self.confirm_button],
        )
        self.body = ScrollContainer(
            style=Pack(flex=5),
            content=self.form.widget,
        )
        self.full_contents = get_container(
            V, END_ACROSS,
            children=[self.body, self.options_container]
        )
        if sys.platform == "win32":
            self.full_contents.style.background_color = "#F9F9F9"
            self.form.widget.style.background_color = "#F9F9F9"

    def handle_confirm_permission(self, widget):
        """App behaviour when the user interacts with any of the fields of
        `customer_data_form`.
        """
        if self.form.required_fields_are_filled():
            self.confirm_button.enabled = True
        else:
            self.confirm_button.enabled = False
        self.undo_button.enabled = True

    def undo_changes(self, widget: Button):
        self.undo_button.enabled = False
        self.confirm_button.enabled = False
        self.form.clear()
        self.form.add_table_fields(self.SELECTED_CUSTOMER)

    def confirm_changes(self, widget):
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

