
from .base import SimpleProbe

class GtkProbe(SimpleProble):

    @property
    def width(self):
        return self.native.get_allocated_width()

    @property
    def height(self):
        return self.native.get_allocated_height()
