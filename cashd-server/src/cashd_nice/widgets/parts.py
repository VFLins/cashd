def notify_error(ui, message: str):
    ui.notify(message, color="negative", icon="cancel", position="bottom-left")


def notify_success(ui, message: str):
    ui.notify(message, color="positive", icon="check", position="bottom-left")


class DefaultHeader:
    HEADER_ENTRIES = [
        ("/assets/SVG_TransacaoBranco.svg", "Transações", "/"),
        ("/assets/SVG_ContasBranco.svg", "Novo cliente", "/customer"),
        ("/assets/SVG_DadosBranco.svg", "Estatísticas", "/stats"),
        ("/assets/SVG_ConfiguracaoBranco.svg", "Configurações", "/config"),
    ]

    def __init__(self, ui, selected_entry: int):
        default_frontmatter(ui)
        with ui.header(elevated=True) as header:
            header.style("background-color: #cadfe7")
            header.classes("gap-0")
            with ui.row() as default_block:
                default_block.classes("!hidden md:!flex w-full")
                for i, entry in enumerate(self.HEADER_ENTRIES):
                    if i == selected_entry:
                        with ui.button().props("unelevated"):
                            btn_image = ui.image(entry[0])
                            btn_image.classes("rounded-full size-8 mr-3 mt-1 mb-1")
                            btn_label = ui.label(entry[1])
                            btn_label.classes("text-base")
                            btn_label.style(
                                "font-family: 'Saira Semibold'; " "text-transform: none"
                            )
                    else:
                        with ui.button() as enabled_button:
                            enabled_button.on("click", self.navigate_to(ui, entry[2]))
                            enabled_button.props("flat")
                            btn_image = ui.image(entry[0])
                            btn_image.classes("rounded-full size-8 mr-3 mt-1 mb-1")
                            btn_label = ui.label(entry[1])
                            btn_label.classes("text-base")
                            btn_label.style(
                                "font-family: 'Saira Semibold'; "
                                "text-transform: none; "
                                "color: black;"
                            )
            with ui.row(align_items="center") as mobile_block:
                mobile_block.classes("md:!hidden w-full flex-nowrap")
                header_image = ui.image(self.HEADER_ENTRIES[selected_entry][0])
                header_image.classes("rounded-full size-12 select-none")
                header_label = ui.label(self.HEADER_ENTRIES[selected_entry][1])
                header_label.classes("text-2xl select-none truncate")
                header_label.style(
                    "font-family: 'Saira Semibold'; "
                    "text-transform: none; "
                    "color: #478eff;"
                )
                ui.space()
                with ui.button(icon="menu"):
                    with ui.menu() as menu:
                        for i, entry in enumerate(self.HEADER_ENTRIES):
                            if i == selected_entry:
                                continue
                            with ui.menu_item(on_click=self.navigate_to(ui, entry[2])):
                                with ui.row().classes("items-center gap-2 no-wrap"):
                                    ui.image(entry[0]).classes(
                                        "rounded-full size-8 mr-3"
                                    )
                                    ui.label(entry[1]).classes(
                                        "whitespace-nowrap select-none"
                                    )

    def navigate_to(self, ui, url: str):
        return lambda: ui.navigate.to(url)


def default_frontmatter(ui):
    """Default frontmatter configuration applied to every page where the DefaultHeader
    is applied
    """
    ui.add_head_html("""
    <style>
        .no-margin-scroll .q-scrollarea__content {
            padding: 0 !important;
        }
    </style>
    """)
    ui.add_css("""
    @font-face {
        font-family: 'Saira Semibold';
        src: url('/assets/Saira-SemiBold.ttf') format('truetype');
        font-weight: normal;
        font-style: normal;
    }
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
    ui.query("body").style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")
    ui.colors(primary="#478eff", secondary="gray", accent="#d3d7d9")
