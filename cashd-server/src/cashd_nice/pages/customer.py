from cashd_core.const import ESTADOS
from cashd_core.data import tbl_clientes, get_default_customer
from cashd_nice.widgets.parts import DefaultHeader, notify_success, notify_error


class page:
    def default_input(self, label: str):
        return self.ui.input(label, on_change=self.enable_insert).props("outlined dense").classes("w-72")

    def select_input(self, options: list[str], label: str):
        return (
            self.ui.select(options, label=label)
            .props("outlined dense")
            .classes("w-72")
        )

    def __init__(self, ui):
        self.ui = ui
        ui.colors(primary="#478eff", secondary="#d3d7d9")
        ui.query("body").style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")
        DefaultHeader(ui=ui, selected_entry=1)
        with ui.column(align_items="center").classes("w-full"):
            with ui.grid().classes("h-full center-items sm:grid-cols-2"):
                self.firstname = self.default_input("Nome*")
                self.lastname = self.default_input("Sobrenome*")
                self.nickname = self.default_input("Apelido")
                self.phonenumber = self.default_input("Telefone")
                self.address = self.default_input("Endereço")
                self.district = self.default_input("Bairro")
                self.city = self.default_input("Cidade")
                self.state = self.select_input(options=ESTADOS, label="Estado")
            with ui.row().classes("w-72 md:w-144"):
                ui.space()
                ui.button("Restaurar", icon="refresh", on_click=self.reset).props("flat")
                self.insert_button = ui.button("Criar", icon="add", on_click=self.add_customer)
        self.reset()

    def add_customer(self):
        try:
            customer = tbl_clientes(
                PrimeiroNome=self.firstname.value,
                Sobrenome=self.lastname.value,
                Apelido=self.nickname.value,
                Telefone=self.phonenumber.value,
                Endereco=self.address.value,
                Bairro=self.district.value,
                Cidade=self.city.value,
                Estado=self.state.value,
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
                f"{customer.NomeCompleto} cadastrado com sucesso",
            )
            self.reset()

    def reset(self):
        customer = get_default_customer()
        self.firstname.set_value(customer.PrimeiroNome)
        self.lastname.set_value(customer.Sobrenome)
        self.nickname.set_value(customer.Apelido)
        self.phonenumber.set_value(customer.Telefone)
        self.address.set_value(customer.Endereco)
        self.district.set_value(customer.Bairro)
        self.city.set_value(customer.Cidade)
        self.state.set_value(customer.Estado)

    def enable_insert(self):
        required_fields = [self.firstname, self.lastname, self.phonenumber, self.city, self.state]
        form_is_ready = all((f.value is not None) and (len(f.value) > 0) for f in required_fields)
        print(form_is_ready)
        if getattr(self, "insert_button", None) is not None:
            if form_is_ready:
                self.insert_button.enable()
            else:
                self.insert_button.disable()

