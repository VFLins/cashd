from datetime import date, datetime
from typing import Any

from cashd_core.fmt import StringToCurrency
from cashd_core.const import ESTADOS
from cashd_core.data import CustomerListSource, tbl_clientes, tbl_transacoes
from cashd.widgets.parts import DefaultHeader, notify_error, notify_success
from cashd.widgets.custom import DetailedList
from cashd.widgets.dialogs import DeleteTransactionDialog
from cashd.const import now


class subpage_transac:
    def __init__(self, ui, on_add=None):
        with ui.column(align_items="start"):
            self.date_input = ui.date_input(
                "Data", value=date.today().strftime("%d/%m/%Y")
            )
            self.date_input.picker.props("mask='DD/MM/YYYY' minimal")
            self.date_input.props("outlined dense").classes("w-full")
            self.value_input = ui.input("Valor", placeholder="0,00")
            self.value_input.props("outlined dense").classes("w-full")
            self.value_input.bind_label_from(
                self.value_input, "value", self.upd_value_input_label
            )
            self.buton = ui.button("Inserir", on_click=on_add)

    @property
    def date(self) -> date:
        value = self.date_input.value
        dt = datetime.strptime(value, "%d/%m/%Y")
        return date(dt.year, dt.month, dt.day)

    @date.setter
    def date(self, value: date):
        self.date_input.value = value.strftime("%d/%m/%Y")

    def upd_value_input_label(self, value: str):
        if value == "":
            return "Valor"
        fmt = StringToCurrency(value)
        return f"Valor: {fmt.display_value}"


class subpage_history:
    def __init__(self, ui, app, customer: tbl_clientes, on_delete=None):
        self.customer = customer
        self.delete_transaction_dialog = DeleteTransactionDialog(ui, app)
        cols = [
            {"name": "data", "label": "Data", "field": "data"},
            {"name": "valor", "label": "Valor (R$)", "field": "valor"},
        ]
        if on_delete is not None:
            cols = [{"name": "action", "label": ""}] + cols

        with ui.column(align_items="end").classes("w-60 md:w-90"):
            ui.button("Imprimir", icon="print")
            self.table = ui.table(
                row_key="id",
                columns=cols,
                rows=list(customer.Transacs),
            )
            self.table.props(
                "dense no-data-label='Nenhuma transação para este cliente'"
            )
            self.table.classes("self-center w-70 md:w-90")
            self.table.style("max-height: calc(100svh - 410px);")
            if on_delete is not None:
                with self.table.add_slot("body-cell-action"):
                    with self.table.cell("action"):
                        del_button = ui.button(icon="delete").props(
                            "flat size=sm dense"
                        )
                        del_button.on(
                            "click",
                            js_handler="() => emit(props.row.id)",
                            handler=lambda e: on_delete(e.args),
                        )

    def change_customer(self, customer: tbl_clientes):
        self.customer = customer
        self.table.rows = list(customer.Transacs)


class subpage_info:
    def __init__(self, ui, customer: tbl_clientes | None = None, on_update=None):
        with ui.row().classes("no-wrap w-70 md:w-90"):
            ui.space()
            ui.button("Restaurar", icon="refresh", on_click=self.reset).props("flat")
            ui.button("Salvar", icon="check", on_click=on_update)
        with ui.scroll_area().classes("no-margin-scroll") as scroll:
            scroll.style("height: calc(100svh - 410px);")
            with ui.grid().classes("w-full h-full md:grid-cols-2"):
                self.firstname = (
                    ui.input("Nome*").props("outlined dense").classes(f"w-full")
                )
                self.lastname = (
                    ui.input("Sobrenome*").props("outlined dense").classes(f"w-full")
                )
                self.nickname = (
                    ui.input("Apelido").props("outlined dense").classes(f"w-full")
                )
                self.phonenumber = (
                    ui.input("Telefone").props("outlined dense").classes(f"w-full")
                )
                self.address = (
                    ui.input("Endereço").props("outlined dense").classes(f"w-full")
                )
                self.district = (
                    ui.input("Bairro").props("outlined dense").classes(f"w-full")
                )
                self.city = (
                    ui.input("Cidade*").props("outlined dense").classes(f"w-full")
                )
                self.state = (
                    ui.select(ESTADOS, value=ESTADOS[0], label="Estado*")
                    .props("outlined dense")
                    .classes(f"w-full")
                )
        if customer is not None:
            self.customer = customer
            self.load(customer)

    def load(self, customer: tbl_clientes):
        self.customer = customer
        self.firstname.set_value(customer.PrimeiroNome)
        self.lastname.set_value(customer.Sobrenome)
        self.nickname.set_value(customer.Apelido)
        self.phonenumber.set_value(customer.Telefone)
        self.address.set_value(customer.Endereco)
        self.district.set_value(customer.Bairro)
        self.city.set_value(customer.Cidade)
        self.state.set_value(customer.Estado)

    def reset(self):
        if self.customer is not None:
            self.load(self.customer)


class CustomerInfo:
    def __init__(self, ui, field: str, value: str):
        with ui.row().classes("no-wrap gap-1") as self.block:
            self.field = ui.label(f"{field}:").classes("select-none font-bold")
            self.value = ui.label(value).classes("select-none text-nowrap tuncate")

    def set_value(self, text: str):
        """Shorthand to replace the text in `CustomerInfo.value` label."""
        self.value.set_text(text)


class page:
    CUSTOMERS_SOURCE = CustomerListSource()

    @property
    def selected_customer(self) -> tbl_clientes:
        customer_id = self.app.storage.client.get("selected_customer", None)
        customer = tbl_clientes()
        if customer_id is not None:
            customer.read(row_id=customer_id)
        return customer

    @selected_customer.setter
    def selected_customer(self, value: tbl_clientes):
        self.app.storage.client["selected_customer"] = value.Id

    def __init__(self, ui, app):
        self.ui, self.app = ui, app
        DefaultHeader(ui, app, selected_entry="Transações")
        print(f"{now()} Drawing '/' page for {app.storage.browser['id']}")
        with ui.column().classes("w-full gap-0"):
            self.top_section()
            with ui.grid().classes("w-full h-full md:grid-cols-2"):
                self.l_section = self.left_section()
                self.r_section = self.right_section()
        # Ensure the customer_list resets to initial state whenever this page loads
        self.CUSTOMERS_SOURCE.search_text = ""
        self.customer_list.items_list.refresh(no_callback=True)

    def top_section(self):
        ui = self.ui
        with ui.row(align_items="center") as top_section:
            top_section.classes(
                "w-full md:w-[80%] lg:w-[60%] self-center no-wrap bg-blue-1 "
                "rounded shadow px-4 py-2"
            )
            self.section_switcher = ui.button(
                icon="point_of_sale", on_click=self.switch_section_mobile
            )
            with ui.scroll_area().classes("no-margin-scroll w-full h-[4rem]"):
                self.section_switcher.classes("!flex md:!hidden")
                with ui.column().classes("gap-0"):
                    self.selected_customer_name = CustomerInfo(
                        ui, field="Cliente", value="N/S"
                    )
                    self.selected_customer_place = CustomerInfo(
                        ui, field="Local", value="N/S"
                    )
                    self.selected_customer_debt = CustomerInfo(
                        ui, field="Saldo devedor", value="R$ 0,00"
                    )
        return top_section

    def left_section(self):
        ui = self.ui
        with ui.column() as left_section:
            left_section.classes("w-full max-w-2xl self-center mx-auto")
            self.customer_list = DetailedList(
                ui,
                datasource=self.CUSTOMERS_SOURCE,
                keys=["Name", "Place"],
                on_select=self.load_selected_customer,
            )
        return left_section

    def right_section(self):
        ui = self.ui
        with ui.column() as right_section:
            right_section.classes("!hidden md:!flex w-full items-center")
            with ui.tabs().classes("w-full mt-4") as self.tabs:
                self.tabs.props(
                    "no-caps active-color='primary' indicator-color='transparent' "
                    "active-bg-color=blue-1 dense"
                )
                self.tabs.style("font-family: 'Saira Semibold';")
                self.tabs.on_value_change(lambda p: self.handle_tab_change(payload=p))
                transac = ui.tab("Nova transação").classes("bg-gray-100 text-gray-700")
                history = ui.tab("Histórico").classes("bg-gray-100 text-gray-700")
                info = ui.tab("Informações").classes("bg-gray-100 text-gray-700")
                transac.style(
                    "border-top-left-radius: 8px; border-bottom-left-radius: 8px;"
                )
                info.style(
                    "border-top-right-radius: 8px; border-bottom-right-radius: 8px;"
                )
            with ui.tab_panels(self.tabs, value=transac):
                with ui.tab_panel(transac):
                    self.transac = subpage_transac(ui, on_add=self.add_transaction)
                    self.transac.value_input.on("keydown.enter", self.add_transaction)
                with ui.tab_panel(history):
                    self.history = subpage_history(
                        ui,
                        self.app,
                        customer=self.selected_customer,
                        on_delete=self.del_transaction,
                    )
                with ui.tab_panel(info):
                    self.info = subpage_info(
                        ui,
                        customer=self.selected_customer,
                        on_update=self.update_selected_customer,
                    )
        return right_section

    def switch_section_mobile(self):
        match self.section_switcher.props["icon"]:
            case "point_of_sale":
                self.section_switcher.props("icon=person_search")
                # hide left and restore right
                self.l_section.classes("!hidden md:!flex")
                self.r_section.classes(remove="!hidden md:!flex")
                self.r_section.classes("w-full items-center")
            case "person_search":
                self.section_switcher.props("icon=point_of_sale")
                # hide right and restore left
                self.r_section.classes("!hidden md:!flex")
                self.l_section.classes(remove="!hidden md:!flex")

    def load_selected_customer(
        self, data: dict[str, Any] | None, update_list: bool = False
    ):
        customer = tbl_clientes()
        # Send selected customer to storage on user interaction with customer list
        customer_list = getattr(self, "customer_list", None)
        if (customer_list is not None) and (data is not None):
            customer_id: int | None = data.get("Id", None)
            if customer_id is not None:
                customer.read(row_id=customer_id)
            self.selected_customer = customer
            browserid = self.app.storage.browser["id"]
            if update_list:
                customer_list.items_list.refresh(no_callback=True)

        if getattr(self, "tabs", None) is not None:
            self.tabs.set_value("Nova transação")
        # Update selected user indicator
        self.selected_customer_name.set_value(customer.NomeCompleto)
        self.selected_customer_place.set_value(customer.Local)
        self.selected_customer_debt.set_value(f"R$ {customer.Saldo}")
        # Update transaction history
        if getattr(self, "history", None) is not None:
            self.history.change_customer(self.selected_customer)

    def handle_tab_change(self, payload):
        match payload.value:
            case "Informações":
                self.info.load(self.selected_customer)

    def update_selected_customer(self):
        customer = self.selected_customer
        print(customer)
        try:
            customer.PrimeiroNome = self.info.firstname.value
            customer.Sobrenome = self.info.lastname.value
            customer.Apelido = self.info.nickname.value
            customer.Telefone = self.info.phonenumber.value
            customer.Endereco = self.info.address.value
            customer.Bairro = self.info.district.value
            customer.Cidade = self.info.city.value
            customer.Estado = self.info.state.value
            customer.update()
        except Exception as err:
            notify_error(
                self.ui, "Erro ao alterar dados do cliente, verifique os logs."
            )
            raise err
        else:
            notify_success(
                self.ui, f"Dados de {customer.NomeCompleto} alterados com sucesso"
            )
        finally:
            self.load_selected_customer(
                data=self.customer_list.selected_data, update_list=True
            )

    def add_transaction(self):
        date = self.transac.date
        value = StringToCurrency(self.transac.value_input.value)
        if not value.is_valid():
            notify_error(self.ui, value.invalid_reason)
            return
        if self.selected_customer.Id is None:
            notify_error(self.ui, "Nenhum cliente selecionado.")
            return
        try:
            transaction = tbl_transacoes(
                IdCliente=self.selected_customer.Id,
                CarimboTempo=datetime.now(),
                DataTransac=date,
                Valor=value.value,
            )
            transaction.write()
        except Exception as err:
            notify_error(self.ui, "Erro inesperado, verifique o arquivo de log.")
            raise err
        else:
            notify_success(self.ui, f"Transação adicionada com sucesso.")
            self.transac.value_input.set_value("")
            self.transac.date = date.today()
            print(f"{now()} {self.app.storage.browser['id']} added a {transaction=}")
        finally:
            self.load_selected_customer(data=self.customer_list.selected_data)

    async def del_transaction(self, transac_id: int):
        transaction = tbl_transacoes()
        transaction.read(row_id=transac_id)
        await self.history.delete_transaction_dialog.show(transaction)
        self.load_selected_customer(data=self.customer_list.selected_data)
