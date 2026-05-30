class page:
    def __init__(self, ui):
        ui.add_head_html("""
        <style>
            .no-margin-scroll .q-scrollarea__content {
                padding: 0 !important;
            }
        </style>
        """)
        ui.colors(
            primary="#478eff", secondary="#d3d7d9", warning="#d48731", info="#478eff"
        )
        ui.query("body").style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")

        with ui.row(align_items="center") as logo_block:
            logo_block.classes("self-center flex-nowrap")
            ui.image("/assets/PNG_LogoIcone.png").classes("w-10")
            logo_label = ui.label("Cashd")
            logo_label.classes("text-3xl select-none")
            logo_label.style("font-family: 'Saira Semibold'; color: var(--q-primary);")

        with ui.column() as input_block:
            input_block.classes(
                "absolute top-1/2 left-1/2 transform "
                "-translate-x-1/2 -translate-y-2/3"
            )
            ui.label("Faça login para acessar o sistema")
            ui.input(label="Usuário").props("outlined dense")
            ui.input(label="Senha", password=True).props("outlined dense")
            ui.button("Entrar").classes("self-end")
