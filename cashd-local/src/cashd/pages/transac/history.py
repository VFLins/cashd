import sys
import toga
from toga.style import Pack
from typing import Callable

from cashd_core import pdf, data
from cashd.widgets.elems import form_options
from cashd.style.vars import set_col_alignments


class Subsection:
    def __init__(
        self,
        selected_customer: data.tbl_clientes,
        on_delete: Callable[[], None] | None = None,
    ):
        self.SELECTED_CUSTOMER = selected_customer
        self.on_delete = on_delete

        self.table = toga.Table(
            style=Pack(flex=1, width=300),
            data=self.SELECTED_CUSTOMER.Transacs,
            columns=["Data", "Valor (R$)"],
            accessors=("data", "valor"),
            on_select=self.select_transac,
        )
        """Table containing all transactions of the currently selected customer."""
        set_col_alignments(self.table, ["l", "r"])

        self.remove_button = toga.Button(
            "Remover selecionado", enabled=False, on_press=self.remove_transac
        )
        """Button to remove the selected transaction on `transaction_history_table`."""

        self.export_button = toga.Button(
            "Exportar",
            style=Pack(margin_left=10),
            enabled=False,
            on_press=self.export_transac,
        )
        """Button to open the dialog for printing the last few transactions registered
        and current owed amount. This feature is aimed for thermal printers.
        """

        self.options_container: toga.Box = form_options(
            buttons=[self.remove_button, self.export_button],
        )
        self.options_container.style.margin = (10, 0, 5, 0)
        self.options_container.style.width = 300

        self.full_contents = toga.Column(
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

    async def export_transac(self, widget: toga.Button):
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
            info = toga.InfoDialog(
                "Documento criado com sucesso",
                "O documento será aberto em outro aplicativo.",
            )
            await widget.app.dialog(info)
            doc.launch_file()

    async def remove_transac(self, widget: toga.Button):
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
            confirm = toga.ConfirmDialog(
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

