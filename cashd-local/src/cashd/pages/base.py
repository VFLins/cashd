from asyncio import sleep
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
                self.rearrange_widgets()
        except CancelledError:
            return

    @property
    def window_size(self):
        """Returns the window size (w, h) of the window where this section
        `full_contents` is being displayed. Returns default initial size if this
        widget is not assigned to any window.
        """
        app = self.full_contents.app
        if app:
            return app.window_size
        return const.MAIN_WINDOW_SIZE

    def rearrange_widgets(self):
        """Rearranges this section's widgets, should be used to turn this section
        responsive to the window size.
        """
