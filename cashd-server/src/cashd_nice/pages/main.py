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
    with ui.column(align_items="start"):
        dateinput = ui.date_input("Data", value=date.today().strftime("%d/%m/%Y"))
        dateinput.picker.props("mask='DD/MM/YYYY'")
        dateinput.classes("w-60")
        ui.input("Valor", placeholder="0,00").classes("w-60")
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
        ).classes("w-80")
        with table.add_slot("body-cell-action"):
            with table.cell("action"):
                del_button = ui.button(icon="delete").props("flat size=sm dense")
                del_button.on(
                    "click",
                    js_handler="() => emit(props.row.id)",
                    handler=lambda e: ui.notify(f"Excluindo transação id={e.args}")
                )


def subpage_info(ui):
    with ui.grid(columns=2):
        elem_width = 40
        ui.input("Nome*").classes(f"w-{elem_width}")
        ui.input("Sobrenome*").classes(f"w-{elem_width}")
        ui.input("Apelido").classes(f"w-{elem_width}")
        ui.input("Telefone").classes(f"w-{elem_width}")
        ui.input("Endereço").classes(f"w-{elem_width}")
        ui.input("Bairro").classes(f"w-{elem_width}")
        ui.input("Cidade").classes(f"w-{elem_width}")
        ui.select(ESTADOS, value=ESTADOS[0], label="Estado").classes(f"w-{elem_width}")
    with ui.row():
        ui.button("Salvar", icon="check").disable()
        ui.button("Restaurar", icon="refresh").props("flat").disable()


class page:
    def __init__(self, ui):
        self.ui = ui
        ui.colors(primary="#478eff", secondary="#d3d7d9")
        DefaultHeader(ui=ui, selected_entry=0)
        self.top_section()
        with ui.grid().classes("w-full h-full sm:grid-cols-2"):
            self.l_section = self.left_section()
            self.r_section = self.right_section()

    def top_section(self):
        ui = self.ui
        with ui.row(align_items="center") as top_section:
            self.section_switcher = ui.button(
                icon="point_of_sale",
                on_click=self.switch_section_mobile
            )
            self.section_switcher.classes("!flex md:!hidden")
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
        with ui.column().classes("w-full max-w-2xl self-center mx-auto") as left_section:
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
            with ui.tabs().classes("w-full").props("no-caps") as self.tabs:
                transac = ui.tab("Transação")
                history = ui.tab("Histórico")
                info = ui.tab("Informações")
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

