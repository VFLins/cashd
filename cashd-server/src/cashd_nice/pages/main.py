from datetime import date

from cashd_core.const import ESTADOS
from cashd_nice.widgets.parts import DefaultHeader, DetailedList

example_customer_data = [
    {"title": "Fulano De Algo", "subtitle": "Rua Olá, 21"},
    {"title": "Ciclano Felício", "subtitle": "Rua Bom Dia, 122"},
    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
    {
        "title": "Maria de Algum Nome Desnecessariamente Comprido",
        "subtitle": "Rua de Morar se tiver uma casa, 121 - Cidade/AC",
    },
    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
]


def subpage_transac(ui):
    with ui.column(align_items="start"):
        dateinput = ui.date_input("Data", value=date.today().strftime("%d/%m/%Y"))
        dateinput.picker.props("mask='DD/MM/YYYY'")
        dateinput.classes("w-full")
        ui.input("Valor", placeholder="0,00").classes("w-full")
        ui.button("Inserir")


def subpage_history(ui):
    ui.add_head_html("""
        <script>
        function langAgnosticPageIndicator(firstRowIndex, endRowIndex, rowsNumber) {
            return firstRowIndex + '-' + endRowIndex + ' [' + rowsNumber + ']';
        }
        </script>
        """)
    with ui.column(align_items="end").classes("w-60 md:w-90"):
        ui.button("Imprimir", icon="print")
    table = ui.table(
        row_key="id",
        columns=[
            {"name": "data", "label": "Data", "field": "data"},
            {"name": "valor", "label": "Valor (R$)", "field": "valor"},
            {"name": "action", "label": ""},
        ],
        rows=[
            {"id": 1, "data": "12/10/2024", "valor": "223,30"},
            {"id": 2, "data": "11/01/2025", "valor": "35,50"},
            {"id": 3, "data": "22/03/2024", "valor": "-200,00"},
        ],
    )
    table.props(
        "dense "
        "rows-per-page-label='Linhas por página:' "
        ":pagination-label='langAgnosticPageIndicator' "
        "no-data-label='Nenhuma transação para este cliente'"
    )
    table.classes("self-center w-70 md:w-90")
    table.style("height: calc(100svh - 390px);")
    with table.add_slot("body-cell-action"):
        with table.cell("action"):
            del_button = ui.button(icon="delete").props("flat size=sm dense")
            del_button.on(
                "click",
                js_handler="() => emit(props.row.id)",
                handler=lambda e: ui.notify(f"Excluindo transação id={e.args}"),
            )


def subpage_info(ui):
    with ui.row().classes("no-wrap w-full md:w-90"):
        ui.space()
        ui.button("Restaurar", icon="refresh").props("flat")
        ui.button("Salvar", icon="check")
    with ui.scroll_area().classes("no-margin-scroll") as scroll:
        scroll.style("height: calc(100svh - 400px);")
        with ui.grid().classes("w-full h-full md:grid-cols-2"):
            ui.input("Nome*").classes(f"w-full")
            ui.input("Sobrenome*").classes(f"w-full")
            ui.input("Apelido").classes(f"w-full")
            ui.input("Telefone").classes(f"w-full")
            ui.input("Endereço").classes(f"w-full")
            ui.input("Bairro").classes(f"w-full")
            ui.input("Cidade*").classes(f"w-full")
            ui.select(ESTADOS, value=ESTADOS[0], label="Estado*").classes(f"w-full")


class CustomerInfo:
    def __init__(self, ui, field: str, value: str):
        with ui.row().classes("no-wrap gap-1") as self.block:
            self.field = ui.label(f"{field}:").classes("select-none font-bold")
            self.value = ui.label(value).classes("select-none text-nowrap tuncate")


class page:
    def __init__(self, ui):
        ui.add_head_html("""
        <style>
            .no-margin-scroll .q-scrollarea__content {
                padding: 0 !important;
            }
        </style>
        """)
        ui.query("body").style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")
        self.ui = ui
        ui.colors(primary="#478eff", secondary="#d3d7d9")
        DefaultHeader(ui=ui, selected_entry=0)
        with ui.column().classes("w-full gap-0"):
            self.top_section()
            with ui.grid().classes("w-full h-full md:grid-cols-2"):
                self.l_section = self.left_section()
                self.r_section = self.right_section()

    def top_section(self):
        ui = self.ui
        with ui.row(align_items="center") as top_section:
            top_section.classes(
                "w-full md:w-[80%] lg:w-[60%] self-center no-wrap bg-[#e1ebf0] "
                "rounded shadow-lg px-4 py-2"
            )
            self.section_switcher = ui.button(
                icon="point_of_sale", on_click=self.switch_section_mobile
            )
            with ui.scroll_area().classes("no-margin-scroll w-full h-[4rem]"):
                self.section_switcher.classes("!flex md:!hidden")
                with ui.column().classes("gap-0"):
                    CustomerInfo(
                        ui, field="Cliente", value="Nome Do Cliente Selecionado"
                    )
                    CustomerInfo(ui, field="Local", value="Endereço Dele")
                    CustomerInfo(ui, field="Saldo devedor", value="R$ 1000,00")
        return top_section

    def left_section(self):
        ui = self.ui
        with ui.column().classes(
            "w-full max-w-2xl self-center mx-auto"
        ) as left_section:
            ui.input(label="Pesquisa").classes("w-full")
            DetailedList(ui, items=example_customer_data)
            with ui.scroll_area().classes("h-[2rem] no-margin-scroll w-full items-end"):
                with ui.row(align_items="center").classes("w-full no-wrap"):
                    ui.space()
                    ui.label("900 itens, mostrando 801-900").classes(
                        "select-none truncate"
                    )
                    with ui.row().classes("gap-0 no-wrap"):
                        ui.button(icon="arrow_back").classes("text-xs").props("flat")
                        ui.button(icon="arrow_forward").classes("text-xs").props("flat")
        return left_section

    def right_section(self):
        ui = self.ui
        with ui.column() as right_section:
            right_section.classes("!hidden md:!flex w-full items-center")
            with ui.tabs().classes("w-full mt-4") as self.tabs:
                self.tabs.props(
                    "no-caps active-color='primary' indicator-color='transparent' "
                    "active-bg-color=blue-1 dense"
                )
                transac = ui.tab("Transação").classes("bg-gray-100 text-gray-700")
                history = ui.tab("Histórico").classes("bg-gray-100 text-gray-700")
                info = ui.tab("Informações").classes("bg-gray-100 text-gray-700")
                transac.style(
                    "border-top-left-radius: 8px; border-bottom-left-radius: 8px;"
                )
                info.style(
                    "border-top-right-radius: 8px; border-bottom-right-radius: 8px;"
                )
            with ui.tab_panels(self.tabs, value=transac):
                with ui.tab_panel(transac):
                    subpage_transac(ui)
                with ui.tab_panel(history):
                    subpage_history(ui)
                with ui.tab_panel(info):
                    subpage_info(ui)
        return right_section

    def switch_section_mobile(self):
        match self.section_switcher.props["icon"]:
            case "point_of_sale":
                self.section_switcher.props("icon=person_search")
                self.tabs.set_value("Transação")
                # hide left and restore right
                self.l_section.classes("!hidden md:!flex")
                self.r_section.classes(remove="!hidden md:!flex")
                self.r_section.classes("w-full items-center")
            case "person_search":
                self.section_switcher.props("icon=point_of_sale")
                # hide right and restore left
                self.r_section.classes("!hidden md:!flex")
                self.l_section.classes(remove="!hidden md:!flex")
