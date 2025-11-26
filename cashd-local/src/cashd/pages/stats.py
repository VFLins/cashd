from datetime import datetime, date
from decimal import Decimal
import math
from random import randint

from toga.app import App
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets.box import Box
from toga.widgets.scrollcontainer import ScrollContainer
from toga.widgets.selection import Selection
from toga.widgets.table import Table
from toga.widgets.base import Widget

from cashd_core import data
from cashd import const, style
from cashd.widgets.paginated import PaginatedTable
from .base import BaseSection


def currency(n: float):
    return Decimal(float(n)).quantize(Decimal("0.00"))


VISUALIZATION_OPTIONS = [
    "Histórico de transações",
    "Maiores saldos",
    "Clientes inativos",
    "Balanço",
    "Saldo acumulado total",
]
TIME_GROUP_OPTIONS = [
    "Mensal",
    "Semanal",
    "Diário",
]


class StatisticsSection(BaseSection):

    def __init__(self, app: App):
        super().__init__(app)

        ### widgets ###
        self.visualization_selection = Selection(
            style=style.WIDE_SELECTION,
            items=VISUALIZATION_OPTIONS,
            on_change=self.select_visualization,
        )
        """Dropdown visualization selector. Updates the displayed table on selection."""

        self.time_grouping_selection = Selection(
            style=style.user_input(Selection),
            items=TIME_GROUP_OPTIONS,
            on_change=self.update_data,
            enabled=False,
        )
        """Dropdown time grouping selector.
        - Changes the timestamps of current table's rows on selection, when applicable;
        - Should be disabled when not applicable.
        """

        self.transaction_history_table = PaginatedTable(
            datasource=data.LastTransactionsSource(),
            style=Pack(flex=1, font_size=const.FONT_SIZE,
                       width=const.CONTENT_WIDTH),
            headings=["Data", "Cliente", "Valor"],
        )
        """Table containing data of every transaction registered recently, most recent first."""

        self.highest_amounts_table = PaginatedTable(
            style=Pack(flex=1, font_size=const.FONT_SIZE,
                       width=const.CONTENT_WIDTH),
            headings=["Cliente", "Saldo atual"],
            accessors=["cliente", "saldo_atual"],
            datasource=data.HighestAmountsSource(),
        )
        """Table displaying customers and their respective owed amount, highest first."""

        self.inactive_customers_table = PaginatedTable(
            style=style.TABLE_OF_DATA,
            headings=["Cliente", "Última transação", "Saldo atual"],
            accessors=["cliente", "ultima_transac", "saldo_atual"],
            datasource=data.InactiveCustomersSource(),
        )
        """Table displaying customers and their last transaction date, oldest first."""

        self.transac_balance_table = PaginatedTable(
            style=Pack(flex=1, font_size=const.FONT_SIZE),
            headings=["Data", "Compras", "Abatimentos", "Saldo"],
            accessors=["data", "compras", "abatimentos", "saldo"],
            datasource=data.TransactionBalanceSource(),
        )
        """Table displaying income vs outcome result by date (may be grouped),
        most recent first.
        """

        self.aggregated_amount_table = PaginatedTable(
            style=Pack(flex=1, font_size=const.FONT_SIZE),
            headings=["Data", "Compras", "Abatimentos", "Saldo acumulado"],
            accessors=["data", "compras", "abatimentos", "total"],
            datasource=data.AggregatedAmountSource(),
        )
        """Table displaying the accumulated income vs outcome result by date
        (may be grouped), most recent first.
        """

        ### containers ###
        self.controls_first_row = Box(
            style=Pack(direction="row", align_items="center"),
            children=[
                self.visualization_selection,
                self.time_grouping_selection,
            ],
        )
        self.header = Box(style=style.VERTICAL_BOX,
                          children=[self.controls_first_row])
        self.body = ScrollContainer(
            style=style.HORIZONTAL_BOX, content=self.transaction_history_table.widget
        )
        self.full_contents = Box(
            style=style.FULL_CONTENTS,
            children=[
                self.header,
                self.body,
            ],
        )

    def select_visualization(self, widget: Widget | None = None):
        selected_visualization = self.visualization_selection.value
        if selected_visualization in ["Balanço", "Saldo acumulado total"]:
            self.time_grouping_selection.enabled = True
        else:
            self.time_grouping_selection.enabled = False
        self.change_visualization(selection=selected_visualization)
        self.update_data(widget)

    def change_visualization(self, selection):
        match selection:
            case "Histórico de transações":
                self.body.content = self.transaction_history_table.widget
            case "Maiores saldos":
                self.body.content = self.highest_amounts_table.widget
            case "Clientes inativos":
                self.body.content = self.inactive_customers_table.widget
            case "Balanço":
                self.body.content = self.transac_balance_table.widget
            case "Saldo acumulado total":
                self.body.content = self.aggregated_amount_table.widget
            case _:
                pass

    def update_data(self, widget: Widget | None = None):
        tables = {
            "Histórico de transações": self.transaction_history_table,
            "Maiores saldos": self.highest_amounts_table,
            "Clientes inativos": self.inactive_customers_table,
            "Balanço": self.transac_balance_table,
            "Saldo acumulado total": self.aggregated_amount_table,
        }
        date_freqs = {
            "Mensal": "m",
            "Semanal": "w",
            "Diário": "d",
        }
        selected_view = self.visualization_selection.value
        tbl: PaginatedTable = tables.get(selected_view)
        date_freq = date_freqs.get(self.time_grouping_selection.value)
        tbl._datasource.update_date_format(date_freq)
        print(f"Update displayed table: {selected_view=}, {date_freq=}")
        tbl.refresh()

    def update_data_widgets(self):
        self.select_visualization()
        self.update_data()
