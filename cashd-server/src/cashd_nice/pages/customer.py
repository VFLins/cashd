from cashd_core.const import ESTADOS

from cashd_nice.widgets.parts import DefaultHeader


def page(ui):
    ui.colors(primary="#478eff", secondary="#d3d7d9")
    ui.query("body").style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")
    DefaultHeader(ui=ui, selected_entry=1)
    with ui.column(align_items="center").classes("w-full"):
        with ui.grid().classes("h-full center-items sm:grid-cols-2"):
            elem_width = 72
            ui.input("Nome*").props("outlined dense").classes(f"w-{elem_width}")
            ui.input("Sobrenome*").props("outlined dense").classes(f"w-{elem_width}")
            ui.input("Apelido").props("outlined dense").classes(f"w-{elem_width}")
            ui.input("Telefone").props("outlined dense").classes(f"w-{elem_width}")
            ui.input("Endereço").props("outlined dense").classes(f"w-{elem_width}")
            ui.input("Bairro").props("outlined dense").classes(f"w-{elem_width}")
            ui.input("Cidade").props("outlined dense").classes(f"w-{elem_width}")
            (
                ui.select(ESTADOS, value=ESTADOS[0], label="Estado")
                .props("outlined dense")
                .classes(f"w-{elem_width}")
            )
        with ui.row().classes("w-72 md:w-144"):
            ui.space()
            ui.button("Restaurar", icon="refresh").props("flat").disable()
            ui.button("Criar", icon="add").disable()
