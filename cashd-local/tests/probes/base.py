import asyncio


class SimpleProbe:
    def __init__(self, widget):
        self.widget = widget
        self.impl = widget._impl
        self.native = widget._impl.native

    async def redraw(self, message=None, delay=0.05):
        if message:
            print(message)
        await asyncio.sleep(delay)

    @property
    def width(self):
        return self._width()   # implemente por backend

    @property
    def height(self):
        return self._height()
