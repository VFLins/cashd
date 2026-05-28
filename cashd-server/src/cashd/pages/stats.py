from cashd_core.data import (
    _DataSource,
    LastTransactionsSource,
    TransactionBalanceSource,
    AggregatedAmountSource,
    HighestAmountsSource,
    InactiveCustomersSource,
)
from cashd.widgets.parts import DefaultHeader
import plotly.graph_objects as go
from nicegui import ui

CURRENCY_COLNAMES = [
    "Valor",
    "OwedAmount",
    "Sums",
    "Deductions",
    "Balance",
    "AcumBalance",
]
DATE_COLNAMES = ["Data", "LastTransac"]
DISPLAY_NAMES = {
    "Valor": "Valor (R$)",
    "OwedAmount": "Saldo devedor (R$)",
    "Sums": "Compras (R$)",
    "Deductions": "Abatimentos (R$)",
    "Balance": "Saldo (R$)",
    "AcumBalance": "Saldo acumulado (R$)",
    "Date": "Data",
    "LastTransac": "Última transação (R$)",
}


class Table:
    @property
    def data(self) -> list[dict[str, str]]:
        colnames: list[str] = self.source.SELECT_STMT.selected_columns.keys()
        return [
            {col: getattr(row, col) for col in colnames}
            for row in self.source.current_data
        ]

    @property
    def columns(self) -> list[dict[str, str]]:
        colnames: list[str] = self.source.SELECT_STMT.selected_columns.keys()
        columns = []
        for name in colnames:
            label = DISPLAY_NAMES.get(name, name)
            key = name.lower()
            if name in CURRENCY_COLNAMES:
                columns.append(
                    {"name": key, "label": label, "field": name, "align": "right"}
                )
            else:
                columns.append(
                    {"name": key, "label": label, "field": name, "align": "left"}
                )
        return columns

    @property
    def pagination_text(self) -> str:
        return (
            f"{self.source.nrows} itens, mostrando {self.source.min_idx + 1} "
            f"até {self.source.max_idx}"
        )

    def refresh(self):
        self.table.columns = self.columns
        self.table.rows = self.data
        self.pagination_label.set_text(self.pagination_text)

    def next_page(self):
        self.source.fetch_next_page()
        self.refresh()

    def previous_page(self):
        self.source.fetch_previous_page()
        self.refresh()

    def change_source(self, source: _DataSource):
        self.source = source
        self.refresh()

    def __init__(self, ui, source: _DataSource):
        self.source = source
        self.table = ui.table(columns=self.columns, rows=self.data)
        self.table.classes("self-center !w-full md:!max-w-160").props("dense")
        self.table.style("height: calc(100svh - 240px);")
        with ui.scroll_area().classes("h-[2rem] no-margin-scroll w-full items-end"):
            with ui.row(align_items="center") as pagination_block:
                pagination_block.classes(
                    "w-full md:max-w-160 no-wrap self-center justify-end"
                )
                self.pagination_label = ui.label(self.pagination_text)
                self.pagination_label.classes("select-none truncate")
                with ui.row().classes("gap-0 no-wrap"):
                    (
                        ui.button(icon="arrow_back", on_click=self.previous_page)
                        .classes("text-xs")
                        .props("flat")
                    )
                    (
                        ui.button(icon="arrow_forward", on_click=self.next_page)
                        .classes("text-xs")
                        .props("flat")
                    )


def example_plot(ui):
    example_plot = go.Figure(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 2.5]))
    example_plot.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return ui.plotly(example_plot).classes("h-[100%] w-[90%] center-self")


class page:
    LAST_TRANSACTIONS_SOURCE = LastTransactionsSource()
    TRANSACTION_BALANCE_SOURCE = TransactionBalanceSource()
    AGGREGATED_AMOUNT_SOURCE = AggregatedAmountSource()
    HIGHEST_AMOUNTS_SOURCE = HighestAmountsSource()
    INACTIVE_CUSTOMER_SOURCE = InactiveCustomersSource()
    current_source = LAST_TRANSACTIONS_SOURCE

    def __init__(self, ui):
        self.ui = ui
        DefaultHeader(ui, selected_entry=2)
        self.controls_block()
        with ui.column(align_items="center") as self.displayed_stat:
            self.displayed_stat.classes("w-full h-full")
            self.View = Table(ui, self.current_source)

    def controls_block(self):
        ui = self.ui
        with ui.row(align_items="center") as controls_block:
            controls_block.classes("self-center justify-center")
            with ui.row(align_items="center") as options_block:
                options_block.classes(
                    "rounded border-[primary] shadow py-2 px-4 bg-blue-1"
                )
                self.stat_selector = (
                    ui.select(
                        options=[
                            "Últimas transações",
                            "Balanço",
                            "Balanço acumulado",
                            "Maiores saldos devedores",
                            "Clientes inativos",
                        ],
                        value="Últimas transações",
                        on_change=self.update_view,
                    )
                    .props("outlined dense")
                    .classes("w-48")
                )
                self.freq_selector = (
                    ui.select(
                        options=["Mensal", "Semanal", "Diário"],
                        value="Mensal",
                        on_change=self.update_freq,
                    )
                    .props("outlined dense")
                    .classes("w-28")
                )
                self.freq_selector.bind_visibility_from(
                    self.stat_selector,
                    "value",
                    backward=lambda v: v in ["Balanço", "Balanço acumulado"],
                )
                # self.freq_amount = (
                #     ui.number(label="Meses", value=8, min=3, precision=0, format="%.0f")
                #     .props("outlined dense")
                #     .classes("w-18")
                # )
                # self.freq_amount.bind_visibility_from(
                #     self.stat_selector,
                #     "value",
                #     backward=lambda v: v in ["Balanço", "Balanço acumulado"],
                # )
            # ui.button(icon="refresh", on_click=self.current_stat)
        return controls_block

    def change_displayed_freq(self):
        self.rename_freq_amount()

    # def rename_freq_amount(self):
    #     match self.freq_selector.value:
    #         case "Diário":
    #             self.freq_amount.label = "Dias"
    #         case "Semanal":
    #             self.freq_amount.label = "Semanas"
    #         case _:
    #             self.freq_amount.label = "Meses"
    #     self.freq_amount.update()

    def update_view(self):
        match self.stat_selector.value:
            case "Clientes inativos":
                self.current_source = self.INACTIVE_CUSTOMER_SOURCE
            case "Maiores saldos devedores":
                self.current_source = self.HIGHEST_AMOUNTS_SOURCE
            case "Balanço acumulado":
                self.current_source = self.AGGREGATED_AMOUNT_SOURCE
            case "Balanço":
                self.current_source = self.TRANSACTION_BALANCE_SOURCE
            case _:
                self.current_source = self.LAST_TRANSACTIONS_SOURCE
        self.View.change_source(self.current_source)

    def update_freq(self):
        match self.freq_selector.value:
            case "Diário":
                self.current_source.update_date_format("d")
            case "Semanal":
                self.current_source.update_date_format("w")
            case _:
                self.current_source.update_date_format("m")
        self.View.refresh()

    def next_page(self):
        self.current_source.fetch_next_page()
        self.update_view()

    def previous_page(self):
        self.current_source.fetch_previous_page()
        self.update_view()
