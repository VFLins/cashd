from argon2.exceptions import VerifyMismatchError
from sqlalchemy.exc import StatementError
from nicegui.events import KeyEventArguments
from cashd.widgets.parts import default_frontmatter, notify_error
from cashd.const import now
from cashd import auth


class page:
    def __init__(self, ui, app):
        self.ui, self.app = ui, app
        default_frontmatter(ui)

        with ui.row(align_items="center") as logo_block:
            logo_block.classes("self-center flex-nowrap")
            ui.image("/assets/PNG_LogoIcone.png").classes("w-10")
            logo_label = ui.label("Cashd")
            logo_label.classes("text-3xl select-none")
            logo_label.style("font-family: 'Saira Semibold'; color: var(--q-primary);")

        with ui.column() as input_block:
            input_block.classes(
                "absolute top-1/2 left-1/2 transform "
                "-translate-x-1/2 -translate-y-1/2"
            )
            ui.label("Faça login para acessar o sistema")
            self.user = ui.input(label="Usuário")
            self.user.props("outlined dense")
            self.password = ui.input(label="Senha", password=True)
            self.password.props("outlined dense")
            self.password.on("keydown.enter", self.login)
            ui.button("Entrar", on_click=self.login).classes("self-end")

    def login(self):
        usr, pwd = self.user.value, self.password.value
        try:
            user = auth.verify_login(username=usr, password=pwd)
            role = auth.Role()
            role.read(row_id=user.RoleId)
            if role.RoleName == "Desligado":
                notify_error(self.ui, "Este usuário não pode acessar o Cashd")
                return
        except (StatementError, ValueError, VerifyMismatchError):
            notify_error(self.ui, "Usuário ou senha incorretos")
        else:
            print(f"{now()} {self.app.storage.browser['id']} logged in as '{usr}'")
            self.app.storage.user["userid"] = user.Id
            self.ui.navigate.to("/")
