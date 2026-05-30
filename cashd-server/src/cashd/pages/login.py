class page:
    def __init__(self, ui):
        ui.add_head_html("""
        <style>
            .no-margin-scroll .q-scrollarea__content {
                padding: 0 !important;
            }
        </style>
        """)
        ui.add_css("""
        .nicegui-markdown h1 {
            margin: 16px 0px 0px 0px;
            width: 100%;
            font-size: 20px;
            font-family: 'Saira Semibold';
            color: #478eff;
        }
        .nicegui-markdown h2 {
            margin: 8px 0px 0px 0px;
            margin: 0px;
            font-size: 16px;
            font-weight: bold;
        }
        """)
        ui.colors(
            primary="#478eff", secondary="#d3d7d9", warning="#d48731", info="#478eff"
        )
        ui.query("body").style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")

        with ui.column() as main_block:
            main_block.classes("self-center")
            ui.image("/assets/PNG_LogoIcone.png")
            ui.label("Cashd").classes("text-2xl").style("font-family: 'Saira Semibold'; color: #47eff")
