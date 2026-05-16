from cashd_nice import auth
from sqlalchemy.exc import IntegrityError


def notify_error(ui, message: str):
    ui.notify(message, color="negative", icon="cancel", position="bottom-left")


def notify_success(ui, message: str):
    ui.notify(message, color="positive", icon="check", position="bottom-left")


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

        with ui.tabs().classes("self-center") as tabs:
            tabs.props(
                "no-caps active-color='primary' indicator-color='transparent' "
                "active-bg-color=blue-1 dense"
            )
            existing = ui.tab("Usuários").classes("bg-gray-100 text-gray-700")
            new = ui.tab("Cadastrar usuário").classes("bg-gray-100 text-gray-700")
            existing.style("border-top-left-radius: 8px; border-bottom-left-radius: 8px;")
            new.style("border-top-right-radius: 8px; border-bottom-right-radius: 8px;")
        with ui.tab_panels(tabs, value=existing) as tab_panels:
            tab_panels.classes("self-center w-full md:w-96")
            with ui.tab_panel(existing).classes("items-center w-full"):
                self.existing_user(ui)
            with ui.tab_panel(new).classes("items-center"):
                self.new_user(ui)

    def new_user(self, ui):
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
                "bg-(--q-warning) p-2 w-40 md:w-full "
                "rounded gap-2 no-wrap border shadow"
            )
            ui.icon("priority_high").classes("text-xl")
            label = ui.label(
                "Não perca a senha, o Cashd não pode informar a "
                "senha deste usuário depois de criada."
            )
            label.classes("text-xs text-bold")
        ui.button("Criar", icon="add", on_click=self.add_user)

    def existing_user(self, ui):
        cols = [
            {"name": "username", "label": "Usuário", "field": "username"},
            {"name": "role", "label": "Cargo", "field": "role"},
            {"name": "upd_role", "label": ""},
            {"name": "upd_pass", "label": ""},
        ]
        self.table = ui.table(columns=cols, rows=self.users)
        self.table.props("dense no-data-label='Nenhum usuário cadastrado'")
        self.table.style("max-height: calc(100svh - 140px);")
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

    @property
    def users(self) -> list[dict[str, str]]:
        return [
            {"id": r.Id, "username": r.Username, "role": r.Role}
            for r in self.USER_ROLES_SOURCE.current_data
        ]

    @property
    def role_ids(self) -> list[dict[str, int]]:
        return {r.RoleName: r.Id for r in self.ROLES_SOURCE.current_data}

    @property
    def roles(self) -> list[str]:
        return [r.RoleName for r in self.ROLES_SOURCE.current_data]

    def _clear_fields(self):
        """Returns the original values of the user form."""
        self.username_input.set_value(None)
        self.userrole_input.set_options(self.roles, value=self.roles[0])
        self.pass_input.set_value(None)
        self.pass2_input.set_value(None)

    def _refresh_user_table(self):
        """Fetch the current user data and replaces the data in the user table."""
        self.table.rows = self.users

    def add_user(self):
        ui = self.ui
        if self.pass_input.value != self.pass2_input.value:
            notify_error(ui, "As senhas informadas não são iguais")
            return
        try:
            role_name = self.userrole_input.value
            role_id = self.role_ids[role_name]
            username = self.username_input.value
            password = self.pass_input.value
            user = auth.store_login(role_id, username, password)
        except IntegrityError:
            notify_error(ui, "O nome de usuário informado já existe")
        except KeyError:
            notify_error(ui, f"Nenhum cargo com nome '{role_name}' no banco de dados")
        except ValueError:
            notify_error(ui, f"Id de cargo {role_id} não encontrado no banco de dados")
        else:
            self._clear_fields()
            self._refresh_user_table()
            notify_success(ui, f"Usuário '{user.Username}' criado com sucesso")

