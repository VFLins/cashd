from toga.app import App
from asyncio import sleep, CancelledError

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
            print(app.main_window.size)
            await sleep(2)
            await self.responsive_layout_listener(app=app)
        except CancelledError:
            return
