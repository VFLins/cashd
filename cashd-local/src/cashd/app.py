"""
Local-first application that helps you handle cash flow records quickly!
"""

import asyncio
import webbrowser
from typing import Type
from importlib.metadata import version
from toga import App, Group
from toga.window import MainWindow, Window
from toga.widgets.scrollcontainer import ScrollContainer
from toga.widgets.imageview import ImageView
from toga.widgets.button import Button
from toga.widgets.label import Label
from toga.widgets.box import Column, Row
from toga.command import Command
from toga.style import Pack
from toga.style.pack import ROW

from cashd import pages, const, style


class Cashd(App):
    def startup(self):
        """Construct and show the Toga application."""

        self.main_section = pages.MainSection(app=self)
        self.stats_section = pages.StatisticsSection(app=self)
        self.new_customer_section = pages.CreateCustomerSection(app=self)
        self.conf_section = pages.ConfigSection(app=self)

        self.responsive_layout_task = self.loop.create_task(
            coro=self.main_section.responsive_layout_listener()
        )

        self.main_box = ScrollContainer(
            style=Pack(direction=ROW, flex=1, font_size=const.BIG_FONT_SIZE),
            content=self.main_section.full_contents,
        )

        ###############
        # MAIN WINDOW #
        ###############

        self.main_window = MainWindow(
            title=self.formal_name, size=const.MAIN_WINDOW_SIZE, resizable=True
        )
        self.main_window.min_size = (480, 490)
        self.main_window.content = self.main_box
        group_main = Group("Cashd", order=10)
        group_navigate = Group("Navegar", order=20)
        group_help = Group("Ajuda", order=30)
        self.main_window.toolbar.add(
            Command(
                order=3,
                text="Configurações",
                action=self.set_context_content,
                icon=const.ICON_CONFIG,
                group=group_navigate,
            ),
            Command(
                order=2,
                text="Estatísticas",
                action=self.set_context_content,
                icon=const.ICON_STATS,
                group=group_navigate,
            ),
            Command(
                order=1,
                text="Novo Cliente",
                action=self.set_context_content,
                icon=const.ICON_CONTAS,
                group=group_navigate,
            ),
            Command(
                order=0,
                text="Transações",
                action=self.set_context_content,
                icon=const.ICON_TRANSAC,
                enabled=False,
                group=group_navigate,
            ),
        )
        self.commands[Command.EXIT].text = "Encerrar"
        self.commands[Command.EXIT].group = group_main
        self.commands[Command.ABOUT].text = "Sobre"
        self.commands[Command.ABOUT].group = group_help
        self.commands[Command.VISIT_HOMEPAGE].text = "Documentação"
        self.commands[Command.VISIT_HOMEPAGE].group = group_help
        self.main_window.show()

    # Methods
    async def set_context_content(self, command: Command):
        contents = {
            "Transações": self.main_section,
            "Novo Cliente": self.new_customer_section,
            "Estatísticas": self.stats_section,
            "Configurações": self.conf_section,
        }
        # disable clicked command, enable all others
        for toolbar_command in self.main_window.toolbar:
            if toolbar_command.id == command.id:
                toolbar_command.enabled = False
            else:
                toolbar_command.enabled = True
        # set main_box's contents
        current_section: Type[pages.BaseSection] = contents.get(command.text)
        current_section.update_data_widgets()
        self.main_box.content = current_section.full_contents
        # wait all coroutines to complete
        # https://stackoverflow.com/a/68629884
        self.loop.create_task(self.handle_layout_listener(command=command))
        await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})

    async def handle_layout_listener(self, command: Command):
        coroutines = {
            "Transações": self.main_section.responsive_layout_listener(),
            "Novo Cliente": self.new_customer_section.responsive_layout_listener(),
            "Estatísticas": self.stats_section.responsive_layout_listener(),
            "Configurações": self.conf_section.responsive_layout_listener(),
        }
        try:
            cancelled = self.responsive_layout_task.cancel()
            await self.responsive_layout_task
            if not cancelled:
                print(
                    f"Layout listener de {command.text} concluído: ",
                    self.responsive_layout_task.done(),
                )
        except asyncio.CancelledError:
            print(f"Layout listener de '{command.text}' interrompido.")
        finally:
            coro = coroutines.get(command.text)
            print(f"Iniciando layout listener de '{command.text}'.")
            self.responsive_layout_task = self.loop.create_task(coro)
            await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})

    def about(self):
        """Overrides the default 'About' dialog, displaying a custom message."""
        content_width = 320
        self.about_window = Window(
            title="Sobre o Cashd",
            resizable=False,
            minimizable=False,
            size=(360, 190),
        )

        desc_title = Label("Descrição", style=style.HEADING)
        desc_label = Label(
            "Um aplicativo local-first, que te ajuda a controlar \nsuas vendas no "
            "fiado sem deixar de respeitar a\nprivacidade dos seus dados.",
        )
        desc_block = Column(
            style=Pack(width=content_width), children=[desc_title, desc_label]
        )

        version_title = Label("Versão", style=style.HEADING)
        version_label = Label(f"Cashd v{version('cashd')} | Toga v{version('toga')}")
        version_block = Column(
            style=Pack(width=content_width), children=[version_title, version_label]
        )

        madeby_title = Label("Desenvolvido por", style=style.HEADING)
        madeby_label = ImageView(const.VITORLINS_LOGO, style=Pack(margin=(20, 0)))
        madeby_block = Column(
            style=Pack(width=content_width), children=[madeby_title, madeby_label]
        )

        close_button = Button(
            "OK",
            style=Pack(width=80, margin=(20, 0)),
            on_press=lambda w: self.about_window.close(),
        )
        contact_button = Button(
            "Entre em contato",
            style=Pack(width=140, margin=(20, 5, 0)),
            on_press=lambda w: webbrowser.open("https://vitorlins.com.br/contato/"),
        )
        actions_block = Column(
            style=Pack(width=content_width, align_items="end"),
            children=[Row(children=[contact_button, close_button])],
        )

        full_contents = Column(
            style=Pack(align_items="center"),
            children=[desc_block, version_block, madeby_block, actions_block],
        )

        self.about_window.content = full_contents
        self.about_window.show()


def main():
    return Cashd(
        formal_name="Cashd",
        app_id="br.com.vitorlins.cashd",
        home_page="https://vitorlins.com.br/software/cashd",
    )
