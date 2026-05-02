from datetime import date

from cashd_core.const import ESTADOS
from cashd_nice.widgets import DefaultHeader, DetailedList


example_customer_data = [
    {"title": "Fulano De Algo", "subtitle": "Rua Olá, 21"},
    {"title": "Ciclano Felício", "subtitle": "Rua Bom Dia, 122"},
    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
    {"title": "Maria de Algum Nome Desnecessariamente Comprido", "subtitle": "Rua de Morar se tiver uma casa, 121 - Cidade/AC"},
    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
]

def subpage_transac(ui):
    with ui.column(align_items="end"):
        dateinput = ui.date_input("Data", value=date.today().strftime("%d/%m/%Y"))
        dateinput.picker.props("mask='DD/MM/YYYY'")
        dateinput.classes("w-40")
        ui.input("Valor", placeholder="0,00").classes("w-40")
        ui.button("Inserir")


def subpage_history(ui):
    ui.add_head_html(
        """
        <script>
        function langAgnosticPageIndicator(firstRowIndex, endRowIndex, rowsNumber) {
            return firstRowIndex + '-' + endRowIndex + ' [' + rowsNumber + ']';
        }
        </script>
        """
    )
    with ui.column(align_items="end"):
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
            pagination=5,
        ).props(
            "rows-per-page-label='Linhas por página:' "
            ":pagination-label='langAgnosticPageIndicator'"
        )
        with table.add_slot("body-cell-action"):
            with table.cell("action"):
                del_button = ui.button(icon="delete").props("flat size=0.7em")
                del_button.on(
                    "click",
                    js_handler="() => emit(props.row.id)",
                    handler=lambda e: ui.notify(f"Excluindo transação id={e.args}")
                )


def subpage_info(ui):
    with ui.grid(columns=2):
        ui.input("Nome*").classes("w-40")
        ui.input("Sobrenome*").classes("w-40")
        ui.input("Apelido").classes("w-40")
        ui.input("Telefone").classes("w-40")
        ui.input("Endereço").classes("w-40")
        ui.input("Bairro").classes("w-40")
        ui.input("Cidade").classes("w-40")
        ui.select(ESTADOS, value=ESTADOS[0], label="Estado").classes("w-40")
    with ui.row():
        ui.button(icon="refresh").disable()
        ui.button(icon="check").disable()


class page:
    def __init__(self, ui):
        self.ui = ui
        ui.colors(primary="#478eff", secondary="#d3d7d9")
        DefaultHeader(ui=ui, selected_entry=0)
        self.top_section()
        with ui.grid().classes("w-full h-full sm:grid-cols-2"):
            self.left_section()
            self.right_section()

    def top_section(self):
        ui = self.ui
        with ui.row(align_items="center") as top_section:
            ui.button(icon="add").classes("!flex md:!hidden")
            ui.markdown(
                f"""
                **Cliente:** *Nome do cliente selecionado*<br>
                **Local:** *Endereço dele*<br>
                **Saldo devedor:** R$ 100,00
                """
            ).classes("text-base select-none")
        return top_section

    def left_section(self):
        ui = self.ui
        with ui.column() as left_section:
            left_section.classes("col-grow overflow-hidden")
            ui.input(label="Pesquisa").classes("w-full")
            DetailedList(ui,items=example_customer_data)
            with ui.row(align_items="center").classes("w-full"):
                ui.label("7 itens, mostrando 1-7").classes("select-none")
                ui.space()
                with ui.row().classes("gap-0"):
                    ui.button("anterior").classes("text-xs").props("flat")
                    ui.button("próximo").classes("text-xs").props("flat")
        return left_section

    def right_section(self):
        ui = self.ui
        with ui.column() as right_section:
            right_section.classes("!hidden md:!flex w-full items-center")
            with ui.tabs().classes("w-full").props("no-caps") as tabs:
                transac = ui.tab("Transação")
                history = ui.tab("Histórico")
                info = ui.tab("Informações")
            with ui.tab_panels(tabs, value=transac):
                with ui.tab_panel(transac):
                    subpage_transac(ui)
                with ui.tab_panel(history):
                    subpage_history(ui)
                with ui.tab_panel(info):
                    subpage_info(ui)
        return right_section


