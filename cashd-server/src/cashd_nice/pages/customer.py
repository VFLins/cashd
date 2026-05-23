from cashd_core.const import ESTADOS

from cashd_nice.widgets.parts import DefaultHeader


class page:
    def __init__(self, ui):
        ui.colors(primary="#478eff", secondary="#d3d7d9")
        ui.query("body").style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")
        DefaultHeader(ui=ui, selected_entry=1)
        with ui.column(align_items="center").classes("w-full"):
            with ui.grid().classes("h-full center-items sm:grid-cols-2"):
                elem_width = 72
                self.firstname = ui.input("Nome*").props("outlined dense").classes(f"w-{elem_width}")
                self.lastname = ui.input("Sobrenome*").props("outlined dense").classes(f"w-{elem_width}")
                self.nickname = ui.input("Apelido").props("outlined dense").classes(f"w-{elem_width}")
                self.phonenumber = ui.input("Telefone").props("outlined dense").classes(f"w-{elem_width}")
                self.address = ui.input("Endereço").props("outlined dense").classes(f"w-{elem_width}")
                self.district = ui.input("Bairro").props("outlined dense").classes(f"w-{elem_width}")
                self.city = ui.input("Cidade").props("outlined dense").classes(f"w-{elem_width}")
                self.state = (
                    ui.select(ESTADOS, value=ESTADOS[0], label="Estado")
                    .props("outlined dense")
                    .classes(f"w-{elem_width}")
                )
            with ui.row().classes("w-72 md:w-144"):
                ui.space()
                ui.button("Restaurar", icon="refresh").props("flat").disable()
                ui.button("Criar", icon="add").disable()

    def add_customer(self):
        try:
            customer = tbl_clientes(
                PrimeiroNome=self.firstname.value,
                Sobrenome=self.lastname.value,
                Apelido=self.nickname.value,
                Telefone=self.phonenumber.value,
                Endereco = self.address.value,
                Bairro = self.district.value,
                Cidade = self.city.value,
                Estado = self.state.value,
            )
            customer.write()
        except Exception as err:
            notify_error(
                self.ui, f"Erro ao criar cliente {customer.NomeCompleto}, verifique os logs."
            )
            raise err
        else:
            notify_success(
                self.ui,
                f"Dados de {customer.NomeCompleto} alterados com sucesso",
            )
