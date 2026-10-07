import toga
from toga.app import App
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.dialogs import ConfirmDialog, ErrorDialog, InfoDialog

from cashd_core import data, fmt, pdf

from cashd import const, widgets
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
from cashd.widgets.form import FormField
from cashd.style.compose import mod, ComposedBox
from cashd.widgets.custom import GroupBox
from cashd.widgets.paginated import PaginatedDetailedList
from . import history, info, insert


class TransacSection(BaseSection):
    SELECTED_CUSTOMER = data.tbl_clientes()
    CUSTOMER_LIST = data.CustomerListSource()
    HELP_MSG = "Selecione um cliente para registrar\numa transação."

    def __init__(self, app: App):
        super().__init__(app)

        self.subsection_add_transac = insert.Subsection(
            selected_customer=self.SELECTED_CUSTOMER,
            on_insert=self._upd_selected_info,
        )

        self.subsection_history = history.Subsection(
            selected_customer=self.SELECTED_CUSTOMER,
            on_delete=self._upd_selected_info,
        )

        self.subsection_customer_info = info.Subsection(
            selected_customer=self.SELECTED_CUSTOMER,
            on_update=self._upd_selected_info,
        )

        # widgets: all contexts
        self.help_msg = toga.Label(
            (
                'Cadastre um cliente em "Novo cliente" para\n'
                "começar a registrar transações."
                if data.tbl_clientes().table_is_empty()
                else self.HELP_MSG
            ),
            style=Pack(font_size=10),
        )
        """Text on top of the page displaying information about the currently
        selected customer.
        """

        self.help_msg_block = toga.ScrollContainer(
            vertical=False,
            content=toga.Box(
                style=Pack(align_items="center", direction="row", flex=1),
                children=[self.help_msg]
            ),
        )

        self.actions_button = toga.Button(
            style=Pack(width=50, height=40, margin_left=20),
            id="actions_button",
            icon=const.ICON_USER_OPTS,
            enabled=False,
            on_press=self.set_context_screen,
        )
        """Button that changes context to interact with the selected user."""

        self.return_button = toga.Button(
            style=Pack(width=50, height=40, margin_left=20),
            id="return_button",
            icon=const.ICON_RETURN,
            on_press=self.set_context_screen,
        )
        """Button that returns the user to the context of customer selection."""

        # widgets: 'select' context
        self.customer_selector = PaginatedDetailedList(
            datasource=self.CUSTOMER_LIST,
            on_select=self.select_customer,
            style=Pack(flex=5),
        )
        """Custom Detailed List with a search bar, and page navigation. Displays
        all registered customers.
        """

        # containers: 'options' context
        self.actions_section = toga.OptionContainer(
            style=Pack(flex=5),  # Ensure it spreads along the window height initially
            content=[
                ("Nova transação", self.subsection_add_transac.full_contents),
                ("Histórico", self.subsection_history.full_contents),
                ("Informações", self.subsection_customer_info.full_contents),
            ],
        )

        # main container
        self.head = ComposedBox(
            mod.STRETCH, mod.STRETCH_CONTENT, mod.CENTER_ACROSS, mod.GAP(10),
            children=[self.actions_button, self.help_msg_block]
        )
        """Contents on the topmost part of this section, displaying the selected
        customer's data.
        """
        self.head_block = ComposedBox(
            mod.H, mod.CONTENT_FLEXES(1, 9),
            children=[
                toga.Box(),
                GroupBox(children=[self.head], style=Pack(margin=(20, 0, 30, 0))),
                toga.Box(),
            ]
        )

        self.body = ComposedBox(
            mod.H, mod.STRETCH, mod.CONTENT_FLEXES(1, 9),
            children=[toga.Box(), self.customer_selector.widget, toga.Box()]
        )
        """Contents of most of the interactive part of this section, including
        all controls that interact with user data.
        """

        self.full_contents = toga.Box(
            style=FULL_CONTENTS,
            children=[self.head_block, self.body],
        )

    def set_layout_0(self, w: int):
        """Rearranges this section's widgets in a single-column layout.

        :param w: window width where this layout handling should be based on.
        """
        self.head.replace_children(self.actions_button, self.help_msg_block)
        self.body.replace_children(
            toga.Box(style=Pack(flex=1)),
            self.customer_selector.widget,
            toga.Box(style=Pack(flex=1)),
        )

    def set_layout_1(self, w: int):
        """Rearranges this section's widgets in a two-column layout.

        :param w: window width where this layout handling should be based on.
        """
        # Assign content
        self.head.replace_children(self.help_msg_block)
        self.body.replace_children(
            toga.Box(style=Pack(flex=1)),
            self.customer_selector.widget,
            toga.Box(style=Pack(flex=1)),
            self.actions_section,
            toga.Box(style=Pack(flex=1)),
        )

    def select_customer(self, widget: toga.Selection):
        if widget.selection is None:
            self.subsection_add_transac.amount_input.enabled = False
            self.subsection_history.export_button.enabled = False
            self.actions_button.enabled = False
            return
        print(f"selected: {widget.selection}")
        self.SELECTED_CUSTOMER.read(row_id=widget.selection.id)
        self._upd_selected_info()
        self.subsection_add_transac.amount_input.enabled = True
        self.subsection_history.export_button.enabled = True
        self.actions_button.enabled = True

    def _upd_selected_info(self):
        self.actions_section.current_tab = 0
        if self.SELECTED_CUSTOMER.Saldo == "N/D":
            self.help_msg.text = "Selecione um cliente, depois clique no botão ao lado"
        else:
            self.help_msg.text = (
                f"Nome: {self.SELECTED_CUSTOMER.NomeCompleto}\n"
                f"Local: {self.SELECTED_CUSTOMER.Local}\n"
                f"Saldo devedor: R$ {self.SELECTED_CUSTOMER.Saldo}"
            )
        self.subsection_history.table.data = self.SELECTED_CUSTOMER.Transacs
        self.subsection_customer_info.form.clear()
        self.subsection_customer_info.form.add_table_fields(self.SELECTED_CUSTOMER)

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

    def set_context_screen(self, widget: toga.Button = None):
        """Change between customer selection and customer data management, depending on
        the button clicked.
        """
        if widget.id == "actions_button":
            self.head.replace_children(self.return_button, self.help_msg_block)
            self.body.replace_children(toga.Box(), self.actions_section, toga.Box())
        if widget.id == "return_button":
            self.head.replace_children(self.actions_button, self.help_msg_block)
            self.body.replace_children(
                toga.Box(), self.customer_selector.widget, toga.Box()
            )
            self._clear_customer_selection()

    def _clear_customer_selection(self):
        self.SELECTED_CUSTOMER.clear()
        self.subsection_add_transac.amount_input.enabled = False
        self.subsection_add_transac.confirm_button.enabled = False
        self.subsection_history.table.data = None
        self.subsection_customer_info.form.clear()
        self.help_msg.text = self.HELP_MSG
        self.customer_selector.search_field.value = ""
        self.customer_selector.clear_selection()
        self.actions_button.enabled = False

    async def rearrange_widgets(self):
        w, _ = self.window_size
        # Get a distinct layout ID for every window width, from 0 to len(widths)
        expected_layout_id = 1 if w >= 740 else 0
        current_layout_id = getattr(self, "layout_id", 0)

        if expected_layout_id == current_layout_id:
            return
        print(f"applying layout id={expected_layout_id}")
        # Use one of the predefined widths so the content widths are previsible
        if expected_layout_id == 0:
            self.set_layout_0(w)
        else:
            self.set_layout_1(w)
        self.layout_id = expected_layout_id
