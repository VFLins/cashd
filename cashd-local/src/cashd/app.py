"""
Local-first application that helps you handle cash flow records quickly!
"""

import asyncio
from typing import Type
from toga import App, Group
from toga.window import MainWindow
from toga.widgets.scrollcontainer import ScrollContainer
from toga.command import Command
from toga.style import Pack
from toga.style.pack import ROW

from cashd import pages, const


class Cashd(App):
    def startup(self):
        """Construct and show the Toga application."""

        self.main_section = pages.MainSection()
        self.stats_section = pages.StatisticsSection()
        self.new_customer_section = pages.CreateCustomerSection()
        self.conf_section = pages.ConfigSection()

        self.loop.create_task(coro=self.main_section.window_size_listener())

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
        self.main_window.min_width = 600
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
        await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})


def main():
    return Cashd("Cashd", "com.cashd.vflins")
