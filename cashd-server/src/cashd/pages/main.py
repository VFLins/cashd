import datetime as dt
from typing import Any

from cashd_core.const import ESTADOS, NA_VALUE
from cashd_core.data import CustomerListSource, tbl_clientes, tbl_transacoes
from cashd_core.fmt import StringToCurrency
from cashd_core.pdf.model import invoice

from cashd.const import is_host, safe_download, writelog
from cashd.widgets.custom import DetailedList
from cashd.widgets.dialogs import DeleteTransactionDialog, MessageDialog
from cashd.widgets.parts import DefaultHeader, notify_error, notify_success


class subpage_transac:
    def __init__(self, ui, on_add=None):
        with ui.column(align_items="start"):
            self.date_input = ui.date_input(
                "Data", value=dt.date.today().strftime("%d/%m/%Y")
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
    def date(self) -> dt.date:
        value = self.date_input.value
        date = dt.datetime.strptime(value, "%d/%m/%Y")
        return dt.date(date.year, date.month, date.day)

    @date.setter
    def date(self, value: dt.date):
        self.date_input.value = value.strftime("%d/%m/%Y")

    def upd_value_input_label(self, value: str):
        if value == "":
            return "Valor"
        fmt = StringToCurrency(value)
        return f"Valor: {fmt.display_value}"


class subpage_history:
    def __init__(self, ui, app, customer: tbl_clientes, on_delete=None):
        self.ui, self.app, self.customer = ui, app, customer
        self.delete_transaction_dialog = DeleteTransactionDialog(ui, app)
        cols = [
            {"name": "data", "label": "Data", "field": "data"},
            {"name": "valor", "label": "Valor (R$)", "field": "valor"},
        ]
        if on_delete is not None:
            cols = [{"name": "action", "label": ""}] + cols

        with ui.column().classes("w-60 md:w-90"):
            self.table = ui.table(
                row_key="id",
                columns=cols,
                rows=list(customer.Transacs),
            )
            self.table.props("dense no-data-label='Nenhuma transação registrada'")
            self.table.classes("self-center w-70 md:w-90")
            self.table.style("max-height: calc(100svh - 300px);")
            with self.table.add_slot("top-right"):
                self.export_button = ui.button(
                    "Exportar", icon="description", on_click=self.export_history
                )
                self.export_button.props("flat")
                self.export_button.disable()
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
        if customer.Id is None:
            self.export_button.disable()
        else:
            self.export_button.enable()

    async def export_history(self):
        try:
            assert type(self.customer.Id) is int
            doc = invoice.CustomerTransactions(customer_id=self.customer.Id)
            doc.render()
        except ValueError:
            error_dialog = MessageDialog(
                ui=self.ui,
                app=self.app,
                title="Erro processando conteúdo do documento",
                message="Um conjunto de caractéres inválidos foram encontrados nas "
                "informações da empresa, corrija os dados inseridos em:\n\n"
                "Configurações > Informações da empresa\n\ne tente novamente.",
                msg_type="error",
            )
            await error_dialog.show()
        except AssertionError:
            error_dialog = MessageDialog(
                ui=self.ui,
                app=self.app,
                title="Selecione um cliente",
                message="Um cliente precisa ser selecionado para exportar seu histórico"
                "de transações.",
                msg_type="error",
            )
        else:
            if is_host(self.ui):
                info_dialog = MessageDialog(
                    ui=self.ui,
                    app=self.app,
                    title="Documento criado com sucesso",
                    message="O documento será aberto em outro aplicativo.",
                    msg_type="info",
                )
                await info_dialog.show()
                doc.launch_file()
            else:
                info_dialog = MessageDialog(
                    ui=self.ui,
                    app=self.app,
                    title="Documento criado com sucesso",
                    message="Ao pressionar 'OK', você fará download do arquivo.",
                    msg_type="info",
                )
                await info_dialog.show()
                safe_download(self.ui, str(doc.meta.document_path))


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
                    ui.input("Nome*").props("outlined dense").classes("w-full")
                )
                self.lastname = (
                    ui.input("Sobrenome*").props("outlined dense").classes("w-full")
                )
                self.nickname = (
                    ui.input("Apelido").props("outlined dense").classes("w-full")
                )
                self.phonenumber = (
                    ui.input("Telefone").props("outlined dense").classes("w-full")
                )
                self.address = (
                    ui.input("Endereço").props("outlined dense").classes("w-full")
                )
                self.district = (
                    ui.input("Bairro").props("outlined dense").classes("w-full")
                )
                self.city = (
                    ui.input("Cidade*").props("outlined dense").classes("w-full")
                )
                self.state = (
                    ui.select(ESTADOS, value=ESTADOS[0], label="Estado*")
                    .props("outlined dense")
                    .classes("w-full")
                )
        if customer is not None:
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
        writelog(f"Drawing '/' page for {app.storage.browser['id']}")
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
            self.section_switcher.enabled = False
            self.section_switcher.bind_enabled_from(
                self.app.storage.client,
                "selected_customer",
                backward=lambda i: i is not None,
            )
            with ui.scroll_area().classes("no-margin-scroll w-full h-[4rem]"):
                self.section_switcher.classes("!flex md:!hidden")
                with ui.column() as self.help_msg_block:
                    self.help_msg_block.classes("flex-grow justify-center")
                    with ui.column() as self.instructions:
                        self.instructions.classes("w-full justify-center")
                        if tbl_clientes().table_is_empty():
                            ui.label(
                                'Cadastre um cliente em "Novo cliente" no menu acima '
                                "para começar a registrar transações."
                            )
                        else:
                            wide = ui.label(
                                "Selecione um cliente para registrar uma transação."
                            )
                            wide.classes("!hidden md:!flex")
                            narrow = ui.label(
                                "Selecione um cliente e clique no botão ao lado para "
                                "registrar uma transação."
                            )
                            narrow.classes("!flex md:!hidden")
                    with ui.column().classes("w-full gap-0") as self.selected_info:
                        self.selected_customer_name = CustomerInfo(
                            ui, field="Cliente", value=NA_VALUE
                        )
                        self.selected_customer_place = CustomerInfo(
                            ui, field="Local", value=NA_VALUE
                        )
                        self.selected_customer_debt = CustomerInfo(
                            ui, field="Saldo devedor", value=NA_VALUE
                        )
                        self.selected_info.set_visibility(False)
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
                on_search=self.unselect_customer,
            )
        return left_section

    def right_section(self):
        ui = self.ui
        with ui.column() as right_section:
            right_section.classes("!hidden md:!flex w-full items-center")
            with ui.tabs().classes("w-full mt-4") as self.tabs:
                self.tabs.props(
                    "no-caps active-color='white' indicator-color='transparent' "
                    "active-bg-color='primary' dense"
                )
                self.tabs.style("font-family: 'Saira Semibold';")
                self.tabs.on_value_change(lambda p: self.handle_tab_change(payload=p))
                transac = ui.tab("Nova transação").classes("rounded")
                history = ui.tab("Histórico").classes("rounded mx-1")
                info = ui.tab("Informações").classes("rounded")
            with ui.tab_panels(self.tabs, value=transac).classes("gap-1"):
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
                self.unselect_customer()

    def unselect_customer(self):
        """Removes all references of customer selection, this will force the user to
        select a customer again to perform any further action.
        """
        self.customer_list.unselect()
        self.selected_customer = tbl_clientes()
        self.selected_info.set_visibility(False)
        self.instructions.set_visibility(True)

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
            writelog(f"{customer=} selected by {browserid=}")
            if update_list:
                customer_list.items_list.refresh(no_callback=True)

        if getattr(self, "tabs", None) is not None:
            self.tabs.set_value("Nova transação")
        # Update selected user indicator
        self.selected_customer_name.set_value(customer.NomeCompleto)
        self.selected_customer_place.set_value(customer.Local)
        self.selected_customer_debt.set_value(f"R$ {customer.Saldo}")
        if self.selected_customer.Saldo != NA_VALUE:
            self.instructions.set_visibility(False)
            self.selected_info.set_visibility(True)
        # Update transaction history
        if getattr(self, "history", None) is not None:
            self.history.change_customer(self.selected_customer)

    def handle_tab_change(self, payload):
        match payload.value:
            case "Informações":
                self.info.load(self.selected_customer)

    def update_selected_customer(self):
        customer = self.selected_customer
        try:
            customer.PrimeiroNome = self.info.firstname.value
            customer.Sobrenome = self.info.lastname.value
            customer.Apelido = self.info.nickname.value
            customer.Telefone = self.info.phonenumber.value
            customer.Endereco = self.info.address.value
            customer.Bairro = self.info.district.value
            customer.Cidade = self.info.city.value
            customer.Estado = self.info.state.value
            customer.update() # may raise AttributeError if Id is not defined.
        except AttributeError:
            notify_error(self.ui, "Nenhum cliente selecionado.")
        except Exception:
            notify_error(
                self.ui, "Erro ao alterar dados do cliente, verifique os logs."
            )
            raise
        else:
            browserid = self.app.storage.browser["id"]
            writelog(f"{browserid} updated {customer=}")
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
                CarimboTempo=dt.datetime.now(),
                DataTransac=date,
                Valor=value.value,
            )
            transaction.write()
        except Exception:
            notify_error(self.ui, "Erro inesperado, verifique o arquivo de log.")
            raise
        else:
            notify_success(self.ui, "Transação adicionada com sucesso.")
            self.transac.value_input.set_value("")
            self.transac.date = date.today()
            writelog(f"{self.app.storage.browser['id']} added a {transaction=}")
        finally:
            self.load_selected_customer(data=self.customer_list.selected_data)

    async def del_transaction(self, transac_id: int):
        transaction = tbl_transacoes()
        transaction.read(row_id=transac_id)
        await self.history.delete_transaction_dialog.show(transaction)
        self.load_selected_customer(data=self.customer_list.selected_data)
