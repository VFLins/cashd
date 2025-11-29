from asyncio import sleep, CancelledError
from toga.app import App
from cashd import const


class BaseSection:
    """Includes default methods for any custom section."""

    def __init__(self, app: App):
        """Define all dynamic widgets and containers of this section."""
        self.app = app

    def update_data_widgets(self):
        """Updates all data widgets of this section from their respective data
        sources. Called when switching from another section to current section.
        """

    async def responsive_layout_listener(self):
        """Listens to the window size constantly, applying necessary transformations
        to this section's layout.
        """
        while True:
            try:
                await sleep(1 / 30)
                self.ensure_window_size()
                self.rearrange_widgets()
            except CancelledError:
                break
                raise

    @property
    def window_size(self) -> tuple[int, int]:
        """Returns the window size (w, h) of the `app`'s main window, or the default
        window size when the former is not found.
        """
        try:
            return self.app.main_window.size
        except AttributeError:
            return const.MAIN_WINDOW_SIZE

    def rearrange_widgets(self):
        """Rearranges this section's widgets, should be used to turn this section
        responsive to the window size.
        """
        print(self, self.window_size)

    def ensure_window_size(self):
        """Restores window size to a value above the minimum values defined at
        the application's main window's `min_height` and `min_width`.
        """
        width, height = self.window_size
        min_width, min_height = self.app.main_window.min_size
        new_width = max(min_width, width)
        new_height = max(min_height, height)
        if not all([(new_width == width), (new_height == height)]):
            self.app.main_window.size = (new_width, new_height)
