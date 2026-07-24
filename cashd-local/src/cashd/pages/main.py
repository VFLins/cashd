import re
import sys
import datetime as dt
from sqlalchemy import exc
from typing import Callable

from toga import Widget
from toga.app import App
from toga.style import Pack
from toga.style.pack import COLUMN
from toga.dialogs import ConfirmDialog, ErrorDialog, InfoDialog
from toga.widgets.box import Box, Column
from toga.widgets.label import Label
from toga.widgets.table import Table
from toga.widgets.button import Button
from toga.widgets.divider import Divider
from toga.widgets.selection import Selection
from toga.widgets.textinput import TextInput
from toga.widgets.scrollcontainer import ScrollContainer
from toga.widgets.optioncontainer import OptionContainer

from cashd_core import data, fmt, pdf

from cashd import const, widgets
from cashd.style.compose import (
    get_container,
    H_CENTER_CONTENT,
    V_CENTER_CONTENT,
    H_CENTER,
    V_CENTER,
    STRETCH,
    CONTENT_WIDTH,
    WIDTH,
    N_COLUMNS,
    BG_COLOR,
    FLEX,
    GAP,
    H_GAP,
)
from cashd.style.vars import (
    set_col_alignments,
    input_annotation,
    user_input,
    INLINE_LABEL,
    GENERIC_LABEL,
    FULL_CONTENTS,
    CONTEXT_BUTTON,
    TABLE_OF_DATA,
    PAGE_BODY,
    VERTICAL_BOX,
    FILLING_VERTICAL_BOX,
    HORIZONTAL_BOX,
)
from cashd.pages.base import BaseSection
from cashd.widgets.paginated import PaginatedDetailedList


class SubsectionAddTransac:
    def __init__(
        self,
        selected_customer: data.tbl_clientes,
        on_insert: Callable[[], None] | None = None,
    ):
        self.SELECTED_CUSTOMER = selected_customer
        self.on_insert = on_insert

        self.date_input_form = widgets.HorizontalDateForm()
        """Custom date input form from 'Inserir transação' context."""

        self.amount_label = Label(
            "Valor: R$ 0,00",
            style=input_annotation(),
        )
        """Label that dynamically displays the currency amount that will be
        inserted by the user.
        """

        self.amount_input = TextInput(
            style=user_input(TextInput),
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

        self.confirm_button = Button(
            "Inserir",
            style=CONTEXT_BUTTON,
            enabled=False,
            on_press=self.insert_transaction,
        )
        """Button to write the transaction with date and currency amount inserted
        by the user to the database.
        """

        self.full_contents = Box(
            style=FILLING_VERTICAL_BOX,
            children=[
                self.date_input_form.widget,
                self.amount_label,
                self.amount_input,
                self.confirm_button,
            ],
        )
        if sys.platform == "win32":
            self.full_contents.style.background_color = "#F9F9F9"

    def insert_transaction(self, widget: Button):
        """Register transaction data to the database."""
        amount_input = fmt.StringToCurrency(user_input=self.amount_input.value)
        if not amount_input.is_valid():
            return
        transac_data = data.tbl_transacoes(
            IdCliente=self.SELECTED_CUSTOMER.Id,
            CarimboTempo=dt.datetime.now(),
            DataTransac=self.date_input_form.value,
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


class SubsectionTransacHistory:
    def __init__(
        self,
        selected_customer: data.tbl_clientes,
        on_delete: Callable[[], None] | None = None,
    ):
        self.SELECTED_CUSTOMER = selected_customer
        self.on_delete = on_delete

        self.table = Table(
            style=Pack(flex=1, font_size=const.FONT_SIZE, width=const.FORM_WIDTH),
            data=self.SELECTED_CUSTOMER.Transacs,
            columns=["Data", "Valor (R$)"],
            accessors=("data", "valor"),
            on_select=self.select_transac,
        )
        """Table containing all transactions of the currently selected customer."""
        set_col_alignments(self.table, ["l", "r"])

        self.remove_button = Button(
            "Remover selecionado", enabled=False, on_press=self.remove_transac
        )
        """Button to remove the selected transaction on `transaction_history_table`."""

        self.export_button = Button(
            "Exportar",
            style=Pack(margin_left=10),
            enabled=False,
            on_press=self.export_transac,
        )
        """Button to open the dialog for printing the last few transactions registered
        and current owed amount. This feature is aimed for thermal printers.
        """

        self.options_container: Box = widgets.elems.form_options(
            buttons=[self.remove_button, self.export_button],
        )
        self.options_container.style.margin = (10, 0, 5, 0)

        self.full_contents = Column(
            style=Pack(align_items="center"),
            children=[self.options_container, self.table],
        )
        if sys.platform == "win32":
            self.options_container.style.background_color = "#F9F9F9"
            self.full_contents.style.background_color = "#F9F9F9"

    def select_transac(self, widget):
        self.remove_button.enabled = True
        if widget.selection is None:
            self.remove_button.enabled = False

    async def export_transac(self, widget: Button):
        try:
            doc = pdf.model.invoice.CustomerTransactions(
                customer_id=self.SELECTED_CUSTOMER.Id
            )
            doc.render()
        except ValueError:
            error = ErrorDialog(
                "Erro processando conteúdo do documento",
                "Um conjunto de caractéres inválidos foram encontrados nas "
                "informações da empresa, corrija os dados inseridos em:\n\n"
                "Configurações > Informações da empresa\n\ne tente novamente.",
            )
            await widget.app.dialog(error)
        else:
            info = InfoDialog(
                "Documento criado com sucesso",
                "O documento será aberto em outro aplicativo.",
            )
            await widget.app.dialog(info)
            doc.launch_file()

    async def remove_transac(self, widget: Button):
        try:
            transac_id = self.table.selection.id
        except AttributeError:
            # Will raise this if somehow there aren't any rows
            # selected but the button is enabled and clicked.
            # Doing this, since there is no 'on_unselect' or
            # 'on_lose_focus' trigger.
            widget.enabled = False
        else:
            transac = data.tbl_transacoes()
            transac.read(row_id=transac_id)
            transac_value = f"R$ {transac.Valor/100}".replace(".", ",")
            confirm = ConfirmDialog(
                title="Remover transação?",
                message=f"Data: {transac.DataTransac}\nValor: {transac_value}",
            )
            if await widget.app.dialog(confirm):
                transac.delete()
                if self.on_delete is not None:
                    self.on_delete()
                # clear table before filling to avoid glitches from winforms
                self.table.data = []
                self.table.data = self.SELECTED_CUSTOMER.Transacs
                print(
                    f"Removed {transac_id=} from {self.SELECTED_CUSTOMER.NomeCompleto}"
                )


class SectionCustomerInfo:
    def __init__(
        self,
        selected_customer: data.tbl_clientes,
        on_update: Callable[[], None] | None = None,
    ):
        self.SELECTED_CUSTOMER = selected_customer
        self.on_update = on_update

        self.form = widgets.form.FormHandler(
            n_cols=2,
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

        self.options_container = widgets.elems.form_options(
            width=self.form.widget.width,
            buttons=[self.undo_button, self.confirm_button],
        )
        self.body = Box(
            style=Pack(direction=COLUMN, align_items="center"),
            children=[self.form.widget, self.options_container],
        )
        self.full_contents = ScrollContainer(content=self.body)
        if sys.platform == "win32":
            self.body.style.background_color = "#F9F9F9"

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


class MainSection(BaseSection):
    SELECTED_CUSTOMER = data.tbl_clientes()
    CUSTOMER_LIST = data.CustomerListSource()

    def __init__(self, app: App):
        super().__init__(app)

        self.subsection_add_transac = SubsectionAddTransac(
            selected_customer=self.SELECTED_CUSTOMER,
            on_insert=self._upd_selected_info,
        )

        self.subsection_transac_history = SubsectionTransacHistory(
            selected_customer=self.SELECTED_CUSTOMER,
            on_delete=self._upd_selected_info,
        )

        self.subsection_customer_info = SectionCustomerInfo(
            selected_customer=self.SELECTED_CUSTOMER,
            on_update=self._upd_selected_info,
        )

        # widgets: all contexts
        self.selected_customer_info = Label(
            f"Nome: {const.NA_VALUE}\n"
            f"Local: {const.NA_VALUE}\n"
            f"Saldo devedor: R$ {const.NA_VALUE}",
            style=INLINE_LABEL,
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

        self.help_msg = Label(
            "Selecione um cliente para escolher uma operação",
            style=GENERIC_LABEL,
        )
        """Text displaying help for the current page functionality."""

        self.return_button = Button(
            icon=const.ICON_RETURN,
            id="return_button",
            on_press=self.set_context_screen,
        )
        """Button that returns the user to the context of customer selection."""

        # widgets: 'select' context
        self.customer_selector = PaginatedDetailedList(
            datasource=self.CUSTOMER_LIST,
            on_select=self.select_customer,
            style=TABLE_OF_DATA,
        )
        """Custom Detailed List with a search bar, and page navigation. Displays
        all registered customers.
        """

        # containers: 'options' context
        self.customer_options_section = OptionContainer(
            style=Pack(
                width=const.CONTENT_WIDTH - 5,
                font_size=const.FONT_SIZE,
                margin=(0, 0, 0, 10),
            ),
            content=[
                ("Nova transação", self.subsection_add_transac.full_contents),
                (
                    "Histórico",
                    self.subsection_transac_history.full_contents,
                ),
                ("Informações", self.subsection_customer_info.full_contents),
            ],
        )

        # main container
        self.header_block = Box(style=HORIZONTAL_BOX)
        """Contents on the topmost part of this section, displaying the selected
        customer's data.
        """
        self.body_block = Box(style=HORIZONTAL_BOX)
        """Contents of most of the interactive part of this section, including
        all controls that interact with user data.
        """
        self.head = Box(
            style=Pack(width=1010, direction="row"),
            children=[self.header_block],
        )
        self.body = Box(
            style=Pack(width=1010, direction="row", flex=1),
            children=[self.body_block],
        )
        self.footer = get_container(N_COLUMNS(2), CONTENT_WIDTH(60), WIDTH(600), H_GAP(50), V_CENTER)
        self.footer.add(*[Button(str(i)) for i in range(10)])
        self.full_contents = Box(
            style=FULL_CONTENTS,
            children=[self.head, self.body, self.footer],
        )
        self.set_layout_0()
        self.layout_id: int = 0

    def set_layout_0(self):
        """Returns this section's widgets in a single-column layout."""
        self.header_block.clear()
        self.body_block.clear()
        self.header_block.add(
            self.customer_options_button,
            self.selected_customer_info,
        )
        self.customer_selector.width = const.CONTENT_WIDTH
        self.body_block.add(self.customer_selector.widget)
        self.head.style = VERTICAL_BOX
        self.body.style = PAGE_BODY

    def set_layout_1(self):
        """Returns this section's widgets in a two-column layout."""
        self.header_block.clear()
        self.body_block.clear()
        self.header_block.add(self.selected_customer_info)
        self.body_block.add(
            self.customer_selector.widget, self.customer_options_section
        )
        width = int(const.CONTENT_WIDTH * 2) - 50
        self.customer_selector.width = const.FORM_WIDTH
        self.head.style = Pack(width=width, direction="row")
        self.body.style = Pack(width=width, direction="row", flex=1)

    def select_customer(self, widget: Selection):
        if widget.selection is None:
            self.subsection_add_transac.amount_input.enabled = False
            self.subsection_transac_history.export_button.enabled = False
            self.customer_options_button.enabled = False
            return
        print(f"selected: {widget.selection}")
        self.SELECTED_CUSTOMER.read(row_id=widget.selection.id)
        self._upd_selected_info()
        self.subsection_add_transac.amount_input.enabled = True
        self.subsection_transac_history.export_button.enabled = True
        self.customer_options_button.enabled = True

    def _upd_selected_info(self):
        self.customer_options_section.current_tab = 0
        self.selected_customer_info.text = (
            f"Nome: {self.SELECTED_CUSTOMER.NomeCompleto}\n"
            f"Local: {self.SELECTED_CUSTOMER.Local}\n"
            f"Saldo devedor: R$ {self.SELECTED_CUSTOMER.Saldo}"
        )
        self.subsection_transac_history.table.data = self.SELECTED_CUSTOMER.Transacs
        self.subsection_customer_info.form.clear()
        self.subsection_customer_info.form.add_table_fields(self.SELECTED_CUSTOMER)

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
        """Change between customer selection and customer data management, depending on
        the button clicked.
        """
        if widget.id == "customer_options_button":
            self.header_block.replace(
                old_child=self.customer_options_button,
                new_child=self.return_button,
            )
            self.body_block.replace(
                old_child=self.customer_selector.widget,
                new_child=self.customer_options_section,
            )
        if widget.id == "return_button":
            self.header_block.replace(
                old_child=self.return_button,
                new_child=self.customer_options_button,
            )
            self.body_block.replace(
                old_child=self.customer_options_section,
                new_child=self.customer_selector.widget,
            )
            self._clear_customer_selection()
            self.update_data_widgets()
            self.customer_selector.clear_selection()
        self._refresh_navigation_buttons(selection=widget.id)
        self._refresh_help_message(selection=widget.id)

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

    def _clear_customer_selection(self):
        self.SELECTED_CUSTOMER.clear()
        self.subsection_add_transac.amount_input.enabled = False
        self.subsection_add_transac.confirm_button.enabled = False
        self.subsection_transac_history.table.data = None
        self.subsection_customer_info.form.clear()
        self.selected_customer_info.text = (
            f"Nome: {const.NA_VALUE}\n"
            f"Local: {const.NA_VALUE}\n"
            f"Saldo devedor: R$ {const.NA_VALUE}"
        )
        self.customer_selector.search_field.value = ""

    def update_data_widgets(self):
        self.customer_selector.refresh(self.CUSTOMER_LIST)

    async def rearrange_widgets(self):
        w, h = self.window_size
        expected_layout_id = 0 if (w < 870) else 1
        if expected_layout_id == self.layout_id:
            return
        match expected_layout_id:
            case 0:
                self.set_layout_0()
            case 1:
                self.set_layout_1()
        self.full_contents.clear()
        self.full_contents.add(self.head)
        self.full_contents.add(self.body)
        self.full_contents.style = FULL_CONTENTS
        self.full_contents.refresh()
        self.layout_id = expected_layout_id
