import decimal
import datetime as dt
import re
from sqlalchemy import exc

from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.dialogs import ConfirmDialog
from toga.widgets.box import Box, Column, Row
from toga.widgets.label import Label
from toga.widgets.table import Table
from toga.widgets.button import Button
from toga.widgets.divider import Divider
from toga.widgets.selection import Selection
from toga.widgets.textinput import TextInput
from toga.widgets.scrollcontainer import ScrollContainer
from toga.widgets.optioncontainer import OptionContainer

from cashd import const, data, style, widgets
from cashd.pages.base import BaseSection
from cashd.widgets.paginated import PaginatedDetailedList


class MainSection(BaseSection):
    SELECTED_CUSTOMER = data.tbl_clientes()
    CUSTOMER_LIST = data.CustomerListSource()

    def __init__(self):
        ### widgets: all contexts ###
        self.selected_customer_info = Label(
            f"Nome: {const.NA_VALUE}\n"
            f"Local: {const.NA_VALUE}\n"
            f"Saldo devedor: R$ {const.NA_VALUE}",
            style=style.INLINE_LABEL,
        )
        """Text on top of the page displaying information about the currently
        selected customer.
        """

        self.customer_options_button = Button(
            icon=const.ICON_USER_OPTS,
            id="customer_options_button",
            enabled=False,
            on_press=self.set_context_screen,
        )
        """Button that changes context to interact with the selected user."""

        self.context_separator = Divider(
            style=style.SEPARATOR,
        )
        """Divider that separates the header and the body of the current page."""

        self.help_msg = Label(
            "Selecione um cliente para escolher uma operação",
            style=style.GENERIC_LABEL,
        )
        """Text displaying help for the current page functionality."""

        self.return_button = Button(
            icon=const.ICON_RETURN,
            id="return_button",
            on_press=self.set_context_screen,
        )
        """Button that returns the user to the context of customer selection."""

        self.insert_transac_context_button = Button(
            "Inserir transação",
            id="add_transac_button",
            style=style.CONTEXT_BUTTON,
            enabled=False,
            on_press=self.set_context_screen,
        )
        """Button that switches to 'Inserir transação' context, enabled only if a customer is selected."""

        self.transac_history_context_button = Button(
            "Histórico de transações",
            id="show_transac_button",
            style=style.CONTEXT_BUTTON,
            enabled=False,
            on_press=self.set_context_screen,
        )
        """Button that switches to 'Histórico de transações' context, enabled only if a customer is selected."""

        self.customer_data_context_button = Button(
            "Dados do cliente",
            id="customer_data_button",
            style=style.CONTEXT_BUTTON,
            enabled=False,
            on_press=self.set_context_screen,
        )
        """Button that switches to 'Dados do cliente' context, enabled only if
        a customer is selected.
        """

        ### widgets: 'select' context ###
        self.customer_list_page_elements = PaginatedDetailedList(
            datasource=self.CUSTOMER_LIST,
            on_select=self.on_customer_selection,
            style=style.TABLE_OF_DATA,
        )
        """Custom Detailed List with a search bar, and page navigation. Displays
        all registered customers.
        """
        self.customer_list_page_elements.widget.add(
            self.customer_options_button)

        ### widgets: 'insert' context ###
        self.date_input_controls = widgets.HorizontalDateForm()
        """Custom date input form from 'Inserir transação' context."""

        self.insert_amount_label = Label(
            "Valor: R$ 0,00",
            style=style.input_annotation(),
        )
        """Label that dynamically displays the currency amount that will be
        inserted by the user.
        """

        self.amount_input = TextInput(
            style=style.user_input(TextInput),
            placeholder="0,00",
            on_change=self.update_typed_transaction_amount,
            on_confirm=self.insert_transac_button_click,
        )
        """Text input that only allows integer and decimal numbers. Receives the
        currency amount of the transaction.
        """

        self.insert_transac_button = Button(
            "Inserir",
            style=style.CONTEXT_BUTTON,
            enabled=False,
            on_press=self.insert_transac_button_click,
        )
        """Button to write the transaction with date and currency amount inserted
        by the user to the database.
        """

        ### widgets: 'transac history' context ###
        self.transaction_history_table = Table(
            style=Pack(flex=1, font_size=const.FONT_SIZE),
            data=self.SELECTED_CUSTOMER.Transacs,
            headings=["Data", "Valor"],
            on_select=self.select_transaction,
        )
        """Table containing all transactions of the currently selected customer."""

        self.remove_transaction_button = Button(
            "Remover transação",
            enabled=False,
            style=style.VERTICAL_ALIGNED_BUTTON,
            on_press=self.remove_selected_transaction,
        )
        """Button to remove the selected transaction on `transaction_history_table`."""

        self.print_transaction_history_button = Button(
            "Imprimir",
            enabled=False,
            style=style.VERTICAL_ALIGNED_BUTTON,
        )
        """Button to open the dialog for printing the last few transactions registered
        and current owed amount. This feature is aimed for thermal printers.
        """

        ### widgets: 'customer data' context ###
        self.customer_data_form = widgets.form.FormHandler(
            on_change=self.update_customer_data_field,
            on_change_required=self.update_customer_data_required_field,
        )
        """Multiple text input fields containing the current information of the
        selected customer.
        """

        self.undo_customer_data_changes_button = Button(
            "Desfazer",
            enabled=False,
            on_press=self.undo_customer_data_update,
            style=style.CONTEXT_BUTTON,
        )
        """Button to undo any changes made by the user on `customer_data_form_widgets`.
        Enabled only when any information is changed."""

        self.confirm_customer_data_changes_button = Button(
            "Confirmar",
            enabled=False,
            on_press=self.confirm_customer_data_update,
            style=style.CONTEXT_BUTTON,
        )
        """Button to write any changes made by the user on `customer_data_form_widgets`
        to the database. Enabled only when any information is changed."""

        ### containers: 'insert' context ###
        self.insert_transaction_context_content = Box(
            style=style.FILLING_VERTICAL_BOX,
            children=[
                self.date_input_controls.full_contents,
                Box(
                    style=Pack(
                        width=const.CONTENT_WIDTH,
                        direction="column",
                        alignment="center",
                    ),
                    children=[
                        self.insert_amount_label,
                        self.amount_input,
                        widgets.elems.form_options_container(
                            children=[
                                self.insert_transac_button], alignment="center"
                        ),
                    ],
                ),
            ],
        )
        ### containers: 'transac history' context ###
        self.transac_history_options = Box(
            style=Pack(direction=COLUMN, width=180, flex=1),
            children=[
                self.remove_transaction_button,
                self.print_transaction_history_button,
            ],
        )
        self.transaction_history_context_content = Box(
            style=style.HORIZONTAL_BOX,
            children=[
                self.transaction_history_table,
                self.transac_history_options,
            ],
        )
        ### containers: 'customer data' context ###
        self.customer_data_interaction_buttons = widgets.elems.form_options_container(
            children=[
                self.undo_customer_data_changes_button,
                self.confirm_customer_data_changes_button,
            ],
        )
        self.customer_data_context_content = ScrollContainer(
            content=Box(
                style=Pack(direction=COLUMN, align_items="center",
                           width=const.FORM_WIDTH),
                children=[
                    self.customer_data_form.full_contents,
                    self.customer_data_interaction_buttons,
                ],
            )
        )
        ### containers: 'options' context ###
        self.customer_options_section = OptionContainer(
            style=Pack(width=const.CONTENT_WIDTH -
                       5, font_size=const.FONT_SIZE),
            content=[
                ("Nova transação", self.insert_transaction_context_content),
                ("Histórico de transações", self.transaction_history_context_content),
                ("Informações do cliente", self.customer_data_context_content),
            ],
        )
        ### containers: all contexts ###
        self.context_navigation_buttons = Box(
            style=style.ROW_OF_BUTTONS,
            children=[
                self.return_button,
                self.insert_transac_context_button,
                self.transac_history_context_button,
                self.customer_data_context_button,
            ],
        )
        self.customer_description_section = Box(
            style=style.HORIZONTAL_BOX,
            children=[
                self.customer_options_button,
                self.selected_customer_info,
            ],
        )
        self.header = Box(
            style=style.VERTICAL_BOX,
            children=[
                self.customer_description_section,
            ],
        )
        self.body = ScrollContainer(
            style=style.PAGE_BODY,
            content=self.customer_list_page_elements.widget,
        )

        self.full_contents = Box(
            style=style.FULL_CONTENTS,
            children=[
                self.header,
                self.body,
            ],
        )

    # methods
    def on_customer_selection(self, widget: Selection):
        if widget.selection is None:
            self.SELECTED_CUSTOMER.clear()
            return
        context_buttons = [
            self.customer_data_context_button,
            self.insert_transac_context_button,
            self.transac_history_context_button,
            self.customer_options_button,
        ]
        for button in context_buttons:
            button.enabled = True
        print(f"selected: {widget.selection}")
        self.SELECTED_CUSTOMER.read(row_id=widget.selection.id)
        self._upd_selected_info()

    def on_click_insert(self, widget):
        try:
            valor = int(self.amount_input.value)
        except TypeError:
            print("O campo de valor está vazio")
            return
        if valor == 0:
            print("O valor não pode ser zero")
            return
        if valor > const.MAX_ALLOWED_VALUE:
            print("Valor acima do permitido")
            return
        operation = "adicionou"
        if valor < 0:
            operation = "removeu"
        print(
            f"{self.SELECTED_CUSTOMER.NomeCompleto} "
            f"{operation} R$ {abs(valor)/100:.2f}"
        )
        self.amount_input.value = None

    def _upd_selected_info(self):
        self.selected_customer_info.text = (
            f"Nome: {self.SELECTED_CUSTOMER.NomeCompleto}\n"
            f"Local: {self.SELECTED_CUSTOMER.Local}\n"
            f"Saldo devedor: R$ {self.SELECTED_CUSTOMER.Saldo}"
        )
        self.transaction_history_table.data = self.SELECTED_CUSTOMER.Transacs

    def _search_results(self, search: str):
        if len(search) == 0:
            return const.customers
        search_terms = re.findall(r"\w+", search)

        def is_match(d: dict) -> bool:
            return all(
                re.search(
                    term,
                    f"{d.get('title')} {
                        d.get('subtitle')}",
                    re.IGNORECASE,
                )
                for term in search_terms
            )

        return [d for d in const.customers if is_match(d)]

    def upd_value_label(self, widget):
        value = widget.value
        if (value is None) or (value > const.MAX_ALLOWED_VALUE):
            self.insert_amount_label.text = "Valor: R$ 0,00"
            return
        sign = "-" if value < 0 else ""
        if value != 0:
            self.insert_amount_label.text = (
                f"Valor: {sign} R$ {abs(value)/100:.2f}".replace(".", ",")
            )

    def upd_customer_list(self, widget):
        search = self.customer_search_bar.value
        page_number = self.customer_list_page_handler.current_page
        self.customer_list_page_handler.upd_list_items(search, page_number)
        self.select_customer_list.data = self.customer_list_page_handler.displayed_data
        self.customer_list_pagination_label.text = (
            self.customer_list_page_handler.pagination_label()
        )
        self.select_customer_list.refresh()

    def next_page_customer_list(self, widget):
        self.customer_list_page_handler.next_page()
        widget.enabled = self.customer_list_page_handler.next_page_exists()
        self.customer_list_previous_page_button.enabled = (
            self.customer_list_page_handler.previous_page_exists()
        )
        self.upd_customer_list(widget)

    def previous_page_customer_list(self, widget):
        self.customer_list_page_handler.previous_page()
        if not self.customer_list_page_handler.previous_page_exists():
            widget.enabled = False
        if self.customer_list_page_handler.next_page_exists():
            self.customer_list_next_page_button.enabled = True
        self.upd_customer_list(widget)

    def set_context_screen(self, widget: Button | None = None):
        context_names = {
            "return_button": self.customer_list_page_elements.widget,
            "customer_options_button": self.customer_options_section,
        }
        if not widget:
            return
        context_elem = context_names.get(widget.id)
        if not context_elem:
            return
        if widget.id == "customer_options_button":
            self.customer_description_section.replace(
                old_child=self.customer_options_button,
                new_child=self.return_button,
            )
            self.customer_data_form.clear()
            self.customer_data_form.add_table_fields(self.SELECTED_CUSTOMER)
            self.customer_options_section.current_tab = 0
        if widget.id == "return_button":
            self.customer_description_section.replace(
                old_child=self.return_button,
                new_child=self.customer_options_button,
            )
            self.update_data_widgets()
        self.body.content = context_elem
        self._refresh_navigation_buttons(selection=widget.id)
        self._refresh_help_message(selection=widget.id)
        self._clear_customer_selection(selection=widget.id)

    def _refresh_navigation_buttons(self, selection: str):
        buttons = {
            "return_button": self.return_button,
            "customer_options_button": self.customer_options_button,
        }
        if selection == "return_button":
            for button in buttons.values():
                button.enabled = False
        else:
            for button in buttons.values():
                button.enabled = True
            buttons[selection].enabled = False

    def _refresh_help_message(self, selection: str):
        help_messages = {
            "return_button": "Selecione um cliente para escolher uma operação",
            "add_transac_button": "Insira os dados da transação e confirme",
            "show_transac_button": "Simples consulta de dados de transação",
            "customer_data_button": "Consulte e edite os dados do cliente selecionado",
            "customer_options_button": "Interaja com os dados do cliente selecionado",
        }
        self.help_msg.text = help_messages[selection]

    def _clear_customer_selection(self, selection: str):
        if selection != "return_button":
            return
        self.selected_customer_info.text = (
            f"Nome: {const.NA_VALUE}\n"
            f"Local: {const.NA_VALUE}\n"
            f"Saldo devedor: R$ {const.NA_VALUE}"
        )
        self.customer_list_page_elements.search_field.value = ""

    def update_typed_transaction_amount(self, widget):
        setattr(widget, "value", re.sub(r"[^\d,-]", "", widget.value))
        if widget.value == "":
            self.insert_amount_label.text = f"Valor: R$ 0,00"
            self.insert_transac_button.enabled = False
            return
        try:
            amount = decimal.Decimal(re.sub(",", ".", widget.value))
        except decimal.InvalidOperation:
            self.insert_amount_label.text = "Insira um valor válido"
            self.insert_transac_button.enabled = False
        else:
            self.insert_amount_label.text = f"Valor: R$ {
                amount:.2f}".replace(
                ".", ","
            )
            self.insert_transac_button.enabled = True

    def select_transaction(self, widget):
        self.remove_transaction_button.enabled = True
        if widget.selection is None:
            self.remove_transaction_button.enabled = False

    def update_customer_data_required_field(self, widget: Button):
        if self.customer_data_form.required_fields_are_filled():
            self.confirm_customer_data_changes_button.enabled = True
        else:
            self.confirm_customer_data_changes_button.enabled = False
        self.update_customer_data_field(widget=widget)

    def update_customer_data_field(self, widget: Button):
        self.undo_customer_data_changes_button.enabled = True

    def undo_customer_data_update(self, widget: Button):
        self.undo_customer_data_changes_button.enabled = False
        self.confirm_customer_data_changes_button.enabled = False
        self.customer_data_form.clear()
        self.customer_data_form.add_table_fields(self.SELECTED_CUSTOMER)

    def confirm_customer_data_update(self, widget):
        new_data = data.tbl_clientes(
            Id=self.SELECTED_CUSTOMER.Id, **self.customer_data_form.data
        )
        self.SELECTED_CUSTOMER.fill(new_data)
        try:
            self.SELECTED_CUSTOMER.update()
            self.customer_data_form.clear()
            self.customer_data_form.add_table_fields(self.SELECTED_CUSTOMER)
            print(f"customer data updated to: {new_data}")
        except exc.StatementError as err:
            self.undo_customer_data_update(widget)
            print(f"Alteração proibida: {str(err.args[0])}")

    def update_data_widgets(self):
        self.customer_list_page_elements.refresh(self.CUSTOMER_LIST)

    def insert_transac_button_click(self, widget: Button):
        transac_data = data.tbl_transacoes(
            IdCliente=self.SELECTED_CUSTOMER.Id,
            CarimboTempo=dt.datetime.now(),
            DataTransac=self.date_input_controls.value,
            Valor=int(decimal.Decimal(
                self.amount_input.value.replace(",", ".")) * 100),
        )
        transac_data.write()
        self.insert_transac_button.enabled = False
        self.amount_input.value = ""
        self._upd_selected_info()

    async def remove_selected_transaction(self, widget: Button):
        transac_id = self.transaction_history_table.selection.id
        transac = data.tbl_transacoes()
        transac.read(row_id=transac_id)
        confirm = ConfirmDialog(
            title="Remover transação?",
            message=f"Data: {transac.DataTransac}\nValor: {transac.Valor/100}"
        )
        if await widget.app.dialog(confirm):
            transac.delete()
            self._upd_selected_info()
            # clear table before filling to avoid glitches from winforms
            self.transaction_history_table.data = []
            self.transaction_history_table.data = self.SELECTED_CUSTOMER.Transacs
            print(
                f"Removed {transac_id=} from {
                    self.SELECTED_CUSTOMER.NomeCompleto}"
            )
