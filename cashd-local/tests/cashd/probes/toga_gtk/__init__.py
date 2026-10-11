from tests.cashd.probes.base import SimpleProbe


class PlatformProbe(SimpleProbe):

    @property
    def width(self):
        return self.native.get_allocated_width()

    @property
    def height(self):
        return self.native.get_allocated_height()
