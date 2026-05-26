from cashd_nice import auth
from cashd_nice.widgets.parts import notify_success, notify_error
from cashd_nice.widgets.dialogs import AddUserDialog, UpdateRoleDialog, UpdatePassDialog
from sqlalchemy.exc import IntegrityError


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
        ui.add_head_html(
            """
        <style>
            .no-margin-scroll .q-scrollarea__content {
                padding: 0 !important;
            }
        </style>
        """
        )
        ui.query("body").style("font-family: Inter, 'Segoe UI', Arial, sans-serif;")
        self.ui = ui
        ui.colors(primary="#478eff", secondary="#d3d7d9")
        self.user_dialog = AddUserDialog(ui)
        self._render_contents(ui)

    def _render_contents(self, ui):
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
        await dialog.show()

    def _refresh_user_table(self):
        """Fetch the current user data and replaces the data in the user table."""
        self.table.rows = self.users
