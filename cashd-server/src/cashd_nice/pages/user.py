from cashd_nice import auth
from sqlalchemy.exc import IntegrityError


def notify_error(ui, message: str):
    ui.notify(message, color="negative", icon="cancel", position="bottom-left")


def notify_success(ui, message: str):
    ui.notify(message, color="positive", icon="check", position="bottom-left")


class AddUserDialog:
    ROLES_SOURCE = auth.RoleSource()

    def __init__(self, ui):
        self.ui = ui
        with ui.dialog() as self.dialog, ui.card().classes("fit-content items-center"):
            self.dialog.on("hide", self.cancel)
            with ui.grid().classes("md:grid-cols-2"):
                self.username_input = ui.input(label="Nome de usuário").classes("w-40")
                self.userrole_input = ui.select(
                    label="Tipo de usuário",
                    value=self.roles[0],
                    options=self.roles
                ).classes("w-40")
                self.pass_input = ui.input(
                    label="Senha", password=True, password_toggle_button=True,
                )
                self.pass_input.classes("w-40")
                self.pass2_input = ui.input(
                    label="Repita a senha", password=True, password_toggle_button=True
                )
                self.pass2_input.classes("w-40")
            with ui.row() as warn_block:
                warn_block.classes(
                    "bg-(--q-warning) p-2 w-40 md:w-85 "
                    "rounded gap-2 no-wrap border shadow"
                )
                ui.icon("priority_high").classes("text-xl")
                label = ui.label(
                    "Não perca a senha, o Cashd não pode informar a "
                    "senha deste usuário depois de criada."
                )
                label.classes("text-xs text-bold")
            with ui.row() as buttons_block:
                buttons_block.classes("self-end justify-end")
                ui.button("Cancelar", icon="close", on_click=self.cancel).props("flat")
                ui.button("Criar", icon="add", on_click=self.add_user)

    @property
    def roles(self) -> list[str]:
        return [r.RoleName for r in self.ROLES_SOURCE.current_data]

    @property
    def role_ids(self) -> list[dict[str, int]]:
        return {r.RoleName: r.Id for r in self.ROLES_SOURCE.current_data}

    def add_user(self):
        ui = self.ui
        role_name = self.userrole_input.value
        username = self.username_input.value
        password = self.pass_input.value
        if username.strip() == "":
            notify_error(ui, "Insira um nome de usuário")
            return
        if self.pass_input.value != self.pass2_input.value:
            notify_error(ui, "As senhas informadas não são iguais")
            return
        try:
            role_id = self.role_ids[role_name]
            user = auth.store_login(role_id, username, password)
        except IntegrityError:
            notify_error(ui, "O nome de usuário informado já existe")
        except KeyError:
            notify_error(ui, f"Nenhum cargo com nome '{role_name}' no banco de dados")
        except ValueError:
            notify_error(ui, f"Id de cargo {role_id} não encontrado no banco de dados")
        else:
            self._clear_fields()
            notify_success(ui, f"Usuário '{user.Username}' criado com sucesso")
            self.dialog.submit(None)

    def cancel(self):
        self._clear_fields()
        self.dialog.submit(None)

    async def open(self) -> None:
        return await self.dialog

    def _clear_fields(self):
        """Returns the original values of the user form."""
        self.username_input.set_value(None)
        self.userrole_input.set_options(self.roles, value=self.roles[0])
        self.pass_input.set_value(None)
        self.pass2_input.set_value(None)


class page:
    USER_ROLES_SOURCE = auth.UserRoleSource()
    ROLES_SOURCE = auth.RoleSource()

    def __init__(self, ui):
        ui.add_head_html(
        """
        <style>
            .no-margin-scroll .q-scrollarea__content {
                padding: 0 !important;
            }
        </style>
        """
        )
        ui.query('body').style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")
        self.ui = ui
        ui.colors(primary="#478eff", secondary="#d3d7d9")
        self.user_dialog = AddUserDialog(ui)
        self.existing_user(ui)

    def existing_user(self, ui):
        cols = [
            {"name": "username", "label": "Usuário", "field": "username"},
            {"name": "role", "label": "Cargo", "field": "role"},
            {"name": "upd_role", "label": ""},
            {"name": "upd_pass", "label": ""},
        ]
        self.table = ui.table(columns=cols, rows=self.users)
        self.table.props("dense no-data-label='Nenhum usuário cadastrado'")
        self.table.classes("self-center")
        self.table.style("max-height: calc(100svh - 40px);")
        with self.table.add_slot("body-cell-upd_role"):
            with self.table.cell("upd_role"):
                btn = ui.button(icon="assignment_ind")
                btn.props("flat dense")
                btn.tooltip("Alterar cargo")
                btn.on(
                    "click",
                    js_handler='() => emit(props.row.id)',
                    handler=lambda e: ui.notify(e.args),
                )
                with ui.tooltip():
                    ui.label("Alterar cargo")
        with self.table.add_slot("body-cell-upd_pass"):
            with self.table.cell("upd_pass"):
                btn = ui.button(icon="password")
                btn.props("flat dense")
                btn.on(
                    "click",
                    js_handler='() => emit(props.row.id)',
                    handler=lambda e: ui.notify(e.args),
                )
                with ui.tooltip():
                    ui.label("Alterar senha")
        with self.table.add_slot('top-right'):
            ui.button("Novo usuário", icon="person_add", on_click=self.add_user).props("flat")

    @property
    def users(self) -> list[dict[str, str]]:
        return [
            {"id": r.Id, "username": r.Username, "role": r.Role}
            for r in self.USER_ROLES_SOURCE.current_data
        ]

    async def add_user(self):
        await self.user_dialog.open()
        self._refresh_user_table()

    def _refresh_user_table(self):
        """Fetch the current user data and replaces the data in the user table."""
        self.table.rows = self.users

