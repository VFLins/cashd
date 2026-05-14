from cashd_nice import auth

class page:
    def __init__(self, ui):
        ui.add_head_html(
        """
        <style>
            .no-margin-scroll .q-scrollarea__content {
                padding: 0 !important;
            }
        </style>
        """
        )
        ui.query('body').style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")
        self.ui = ui
        ui.colors(primary="#478eff", secondary="#d3d7d9")

        with ui.tabs().classes("self-center") as tabs:
            new = ui.tab("Novo")
            existing = ui.tab("Cadastrados")
        with ui.tab_panels(tabs, value=new) as tab_panels:
            tab_panels.classes("self-center w-full md:w-96")
            with ui.tab_panel(new).classes("items-center"):
                self.new_user(ui)
            with ui.tab_panel(existing).classes("items-center w-full"):
                self.existing_user(ui)

    def new_user(self, ui):
        with ui.grid().classes("md:grid-cols-2"):
            ui.input(label="Nome de usuário").classes("w-40")
            ui.select(
                label="Tipo de usuário",
                value="Operador",
                options=["Operador", "Supervisor"]
            ).classes("w-40")
            ui.input(label="Senha").classes("w-40")
            ui.input(label="Repita a senha").classes("w-40")
        with ui.row() as warn_block:
            warn_block.classes("bg-(--q-warning) p-2 w-40 md:w-full")
            warn_block.classes("rounded gap-2 no-wrap border shadow")
            ui.icon("priority_high").classes("text-xl")
            ui.label(
                "Não perca a senha, o Cashd não pode informar a "
                "senha deste usuário depois de criada."
            ).classes("text-xs text-bold")
        ui.button("Criar", icon="add")

    def existing_user(self, ui):
        cols = [
            {"name": "username", "label": "Usuário", "field": "username"},
            {"name": "role", "label": "Cargo", "field": "role"},
            {"name": "upd_role", "label": ""},
            {"name": "upd_pass", "label": ""},
        ]
        rows = [
            {"username": "martadecassia", "role": "Operador"},
            {"username": "marcuslima", "role": "Operador"},
            {"username": "joaomateus", "role": "Desligado"},
        ]
        table = ui.table(columns=cols, rows=rows).props("dense")
        table.style("height: calc(100svh - 140px);")
        with table.add_slot("body-cell-upd_role"):
            with table.cell("upd_role"):
                ui.button(icon="assignment_ind").props("flat dense").on(
                    "click",
                    js_handler='() => emit(props.row.id)',
                    handler=lambda e: ui.notify(e.args),
                )
        with table.add_slot("body-cell-upd_pass"):
            with table.cell("upd_pass"):
                ui.button(icon="password").props("flat dense").on(
                    "click",
                    js_handler='() => emit(props.row.id)',
                    handler=lambda e: ui.notify(e.args),
                )
