from cashd_nice import auth
from cashd_nice.widgets.dialogs import AddUserDialog, UpdateRoleDialog
from sqlalchemy.exc import IntegrityError


def notify_error(ui, message: str):
    ui.notify(message, color="negative", icon="cancel", position="bottom-left")


def notify_success(ui, message: str):
    ui.notify(message, color="positive", icon="check", position="bottom-left")


class UpdatePassDialog:
    def __init__(self, ui, user_id):
        self.user_id = user_id
        with ui.dialog() as self.dialog, ui.card():
            title = ui.markdown(f"Nova senha para *`{self.user_name}`*")
            title.classes("text-lg")
            self.pass_input = ui.input(
                label="Nova senha",
                password=True,
                password_toggle_button=True,
            )
            self.pass_input.classes("w-full")
            self.pass2_input = ui.input(
                label="Repita a senha",
                password=True,
                password_toggle_button=True,
            )
            self.pass2_input.classes("w-full")
            with ui.row() as buttons_block:
                buttons_block.classes("self-end justify-end")
                ui.button("Cancelar", icon="close", on_click=self.cancel).props("flat")
                ui.button("Confimar", icon="check", on_click=self.set_pass)

    @property
    def user_name(self) -> str:
        user = auth.User()
        user.read(row_id=self.user_id)
        return user.Username

    async def open(self) -> None:
        return await self.dialog

    def cancel(self):
        pass

    def set_pass(self):
        pass


class page:
    USER_ROLES_SOURCE = auth.UserRoleSource()
    ROLES_SOURCE = auth.RoleSource()
    COLS = [
        {"name": "username", "label": "Usuário", "field": "username"},
        {"name": "role", "label": "Cargo", "field": "role"},
        {"name": "upd_role", "label": ""},
        {"name": "upd_pass", "label": ""},
    ]

    def __init__(self, ui):
        ui.add_head_html("""
        <style>
            .no-margin-scroll .q-scrollarea__content {
                padding: 0 !important;
            }
        </style>
        """)
        ui.query("body").style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")
        self.ui = ui
        ui.colors(primary="#478eff", secondary="#d3d7d9")
        self.user_dialog = AddUserDialog(ui)
        self.existing_user(ui)

    def existing_user(self, ui):
        self.table = ui.table(columns=self.COLS, rows=self.users)
        self.table.props("dense no-data-label='Nenhum usuário cadastrado'")
        self.table.classes("self-center")
        self.table.style("max-height: calc(100svh - 40px);")
        with self.table.add_slot("body-cell-upd_role"):
            with self.table.cell("upd_role"):
                btn = ui.button(icon="assignment_ind")
                btn.props("flat dense")
                btn.on(
                    "click",
                    js_handler="() => emit(props.row.id)",
                    handler=lambda e: self.upd_role(e.args),
                )
                with ui.tooltip():
                    ui.label("Alterar cargo")
        with self.table.add_slot("body-cell-upd_pass"):
            with self.table.cell("upd_pass"):
                btn = ui.button(icon="password")
                btn.props("flat dense")
                btn.on(
                    "click",
                    js_handler="() => emit(props.row.id)",
                    handler=lambda e: self.upd_pass(e.args),
                )
                with ui.tooltip():
                    ui.label("Alterar senha")
        with self.table.add_slot("top-right"):
            ui.button("Novo usuário", icon="person_add", on_click=self.add_user).props(
                "flat"
            )

    @property
    def users(self) -> list[dict[str, str]]:
        return [
            {"id": r.Id, "username": r.Username, "role": r.Role}
            for r in self.USER_ROLES_SOURCE.current_data
        ]

    async def add_user(self):
        await self.user_dialog.show()
        self._refresh_user_table()

    async def upd_role(self, user_id):
        dialog = UpdateRoleDialog(ui=self.ui, user_id=user_id)
        await dialog.show()
        self._refresh_user_table()

    async def upd_pass(self, user_id):
        dialog = UpdatePassDialog(ui=self.ui, user_id=user_id)
        await dialog.open()

    def _refresh_user_table(self):
        """Fetch the current user data and replaces the data in the user table."""
        self.table.rows = self.users
