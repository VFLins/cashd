from .base import SimpleProbe

class GtkProbe(SimpleProble):

    @property
    def width(self):
        return self.native.Width

    @property
    def height(self):
        return self.native.Height
