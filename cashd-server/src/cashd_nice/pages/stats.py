from cashd_nice.widgets.parts import DefaultHeader


import plotly.graph_objects as go
from nicegui import ui


def example_plot(ui):
    example_plot = go.Figure(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 2.5]))
    example_plot.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return ui.plotly(example_plot).classes("h-[100%] w-[90%] center-self")


def example_table(ui):
    ui.add_head_html("""
        <script>
        function langAgnosticPageIndicator(firstRowIndex, endRowIndex, rowsNumber) {
            return firstRowIndex + '-' + endRowIndex + ' [' + rowsNumber + ']';
        }
        </script>
        """)
    data = [
        {
            "id": i,
            "nome": "0, Nome Completo Do Cliente",
            "valor": f"{(i+1)**0.99:.0f},00",
            "data": f"{i**0.7+1:.0f}/12/2025",
        }
        for i in range(100)
    ]
    table = ui.table(
        columns=[
            {"name": "data", "label": "Data", "field": "data"},
            {"name": "nome", "label": "Nome", "field": "nome", "align": "left"},
            {"name": "valor", "label": "Valor", "field": "valor"},
        ],
        rows=data,
        row_key="id",
    )
    table.classes("self-center sm:!w-full md:!w-auto").props(
        "dense "
        "rows-per-page-label='Linhas por página:' "
        ":pagination-label='langAgnosticPageIndicator'"
    )
    table.style("height: calc(100svh - 240px);")
    with ui.scroll_area().classes(
        "h-[2rem] no-margin-scroll sm:w-full md:w-96 items-end"
    ):
        with ui.row(align_items="center").classes("w-full no-wrap"):
            ui.space()
            ui.label("900 itens, mostrando 801-900").classes("select-none truncate")
            with ui.row().classes("gap-0 no-wrap"):
                ui.button(icon="arrow_back").classes("text-xs").props("flat")
                ui.button(icon="arrow_forward").classes("text-xs").props("flat")


class page:
    def __init__(self, ui):
        self.ui = ui
        ui.colors(primary="#478eff", secondary="#d3d7d9")
        ui.query("body").style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")
        ui.add_head_html("""
        <style>
            .no-margin-scroll .q-scrollarea__content {
                padding: 0 !important;
            }
        </style>
        """)
        DefaultHeader(ui, selected_entry=2)
        self.controls_block()
        with ui.column(align_items="center") as self.displayed_stat:
            self.displayed_stat.classes("w-full h-full")
            example_table(self.ui)

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
                    )
                    .props("outlined dense")
                    .classes("w-48")
                )
                self.freq_selector = (
                    ui.select(
                        options=["Mensal", "Semanal", "Diário"],
                        value="Mensal",
                        on_change=self.change_displayed_freq,
                    )
                    .props("outlined dense")
                    .classes("w-28")
                )
                self.freq_selector.bind_visibility_from(
                    self.stat_selector,
                    "value",
                    backward=lambda v: v in ["Balanço", "Balanço acumulado"],
                )
                self.freq_amount = (
                    ui.number(label="Meses", value=8, min=3, precision=0, format="%.0f")
                    .props("outlined dense")
                    .classes("w-18")
                )
                self.freq_amount.bind_visibility_from(
                    self.stat_selector,
                    "value",
                    backward=lambda v: v in ["Balanço", "Balanço acumulado"],
                )
            refresh_button = ui.button(icon="refresh", on_click=self.current_stat)
        return controls_block

    def current_stat(self):
        self.displayed_stat.clear()
        with self.displayed_stat:
            if self.stat_selector.value in ["Balanço", "Balanço acumulado"]:
                example_plot(self.ui)
            else:
                example_table(self.ui)

    def change_displayed_freq(self):
        self.rename_freq_amount()

    def rename_freq_amount(self):
        match self.freq_selector.value:
            case "Diário":
                self.freq_amount.label = "Dias"
            case "Semanal":
                self.freq_amount.label = "Semanas"
            case _:
                self.freq_amount.label = "Meses"
        self.freq_amount.update()
