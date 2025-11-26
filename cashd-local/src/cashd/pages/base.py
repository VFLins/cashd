from asyncio import sleep, CancelledError
from toga.app import App
from cashd import const

class BaseSection:
    """Includes default methods for any custom section."""

    def __init__(self):
        """Define all dynamic widgets and containers of this section."""

    def update_data_widgets(self):
        """Updates all data widgets of this section from their respective data
        sources. Called when switching from another section to current section.
        """

    async def responsive_layout_listener(self, app: App):
        """Listens to the window size constantly, applying necessary transformations
        to this section's layout.
        """
        try:
            while True:
                await sleep(1/30)
                await self.rearrange_widgets(app)
        except CancelledError:
            return

    def read_window_size(self, app: App) -> tuple[int, int]:
        """Returns the window size (w, h) of the `app`'s main window, or the default
        window size when the former is not found.
        """
        try:
            return app.main_window.size
        except AttributeError:
            return const.MAIN_WINDOW_SIZE

    async def rearrange_widgets(self, app: App):
        """Rearranges this section's widgets, should be used to turn this section
        responsive to the window size.
        """
        print(self.read_window_size(app=app))
