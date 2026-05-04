from cashd_core.const import ESTADOS
from cashd_nice.widgets import DefaultHeader


def h1(ui, title: str):
    ui.markdown(f"# {title}").style(
    ).classes("select-none")
    ui.separator().style("background-color: #478eff;")


def h2(ui, title: str):
    ui.markdown(f"## {title}").classes("font-bold").classes("select-none")


def page(ui):
    ui.add_css(
    """
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
    """
    )
    ui.colors(primary="#478eff", secondary="#d3d7d9")
    DefaultHeader(ui, selected_entry=3)
    with ui.column(align_items="left").classes("self-center"):
        h1(ui, "Preferências")
        h2(ui, "Valores padrão no formulário de contas")
        with ui.grid().classes("h-full center-items sm:grid-cols-2"):
            ui.input("Estado")
            ui.input("Cidade")
            ui.select(ESTADOS, value=ESTADOS[0], label="Estado")
        h2(ui, "Linhas por página nas tabelas")
        with ui.grid().classes("h-full center-items sm:grid-cols-2"):
            ui.number(
                label="Clientes [100]", value=100, min=20, precision=0, format="%.0f"
            ).classes("w-32")
            ui.number(
                label="Estatísticas [200]", value=200, min=20, precision=0, format="%.0f"
            ).classes("w-32")
        h1(ui, "Backup")
        h2(ui, "Locais de backup")
        h2(ui, "Ações")


