from cashd_core.const import ESTADOS
from cashd_core.data import tbl_clientes, get_default_customer
from cashd.widgets.parts import DefaultHeader, notify_success, notify_error
from cashd.const import now


class page:
    def default_input(self, label: str, required=False):
        validation = (
            {"Não pode ficar vazio": lambda v: (v is None) or (len(v) > 0)}
            if required
            else {}
        )
        field = (
            self.ui.input(label, on_change=self.enable_insert, validation=validation)
            .props("outlined dense")
            .classes("w-72")
        )
        if required:
            field.required = True
        return field

    def select_input(self, options: list[str], label: str):
        return (
            self.ui.select(options, label=label).props("outlined dense").classes("w-72")
        )

    def __init__(self, ui, app):
        self.ui, self.app = ui, app
        DefaultHeader(ui, app, selected_entry="Novo cliente")
        print(f"{now()} Drawing '/customer' page for {app.storage.browser['id']}")
        with ui.column(align_items="center") as form_block:
            form_block.classes(
                "sm:w-149 absolute sm:top-1/2 left-1/2 transform "
                "-translate-x-1/2 sm:-translate-y-2/3"
            )
            with ui.grid().classes("h-full center-items sm:grid-cols-2"):
                self.firstname = self.default_input("Nome", required=True)
                self.lastname = self.default_input("Sobrenome", required=True)
                self.nickname = self.default_input("Apelido")
                self.phonenumber = self.default_input("Telefone", required=True)
                self.address = self.default_input("Endereço")
                self.district = self.default_input("Bairro")
                self.city = self.default_input("Cidade", required=True)
                self.state = self.select_input(options=ESTADOS, label="Estado")
            with ui.row().classes("w-72 md:w-144 self-end justify-end"):
                ui.button("Restaurar", icon="refresh", on_click=self.reset).props(
                    "flat"
                )
                self.insert_button = ui.button(
                    "Criar", icon="add", on_click=self.add_customer
                )
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
                self.ui,
                f"Erro ao criar cliente {customer.NomeCompleto}, verifique os logs.",
            )
            raise err
        else:
            notify_success(
                self.ui,
                f"{customer.NomeCompleto} cadastrado com sucesso",
            )
            print(f"{now()} {self.app.storage.browser['id']} added a {customer=}")
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
        required_fields = [
            self.firstname,
            self.lastname,
            self.phonenumber,
            self.city,
            self.state,
        ]
        form_is_ready = all(
            (f.value is not None) and (len(f.value) > 0) for f in required_fields
        )
        if getattr(self, "insert_button", None) is not None:
            if form_is_ready:
                self.insert_button.enable()
            else:
                self.insert_button.disable()
