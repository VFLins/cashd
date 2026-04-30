from cashd_nice.widgets import DetailedList


def page(ui):
    ui.label("Hello world!")
    with ui.grid(columns=2).classes("w-full h-full"):
        with ui.column().classes("col-grow overflow-hidden"):
            DetailedList(
                ui=ui,
                items=[
                    {"title": "Fulano De Algo", "subtitle": "Rua Olá, 21"},
                    {"title": "Ciclano Felício", "subtitle": "Rua Bom Dia, 122"},
                    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
                    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
                    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
                    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
                    {"title": "Beltrano Demisclio", "subtitle": "Rua Tchau, 121"},
                ]
            )
            with ui.row():
                ui.label("7 itens, mostrando de 1 a 7")
                ui.button("anterior")
                ui.button("próximo")
        with ui.column().classes("overflow-hidden"):
            with ui.tabs() as tabs:
                transac = ui.tab("Transação")
                history = ui.tab("Histórico")
                info = ui.tab("Informações")
            with ui.tab_panels(tabs, value=transac):
                with ui.tab_panel(transac):
                    ui.label("Aqui se adicionam as transações")
                with ui.tab_panel(history):
                    ui.label("Aqui se vê o histórico de transações")
                with ui.tab_panel(info):
                    ui.label("Aqui se consulta dados do cadastro do cliente")


