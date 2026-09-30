from tests.cashd.probes.base import SimpleProbe


class PlatformProbe(SimpleProbe):

    @property
    def width(self):
        return self.native.Width

    @property
    def height(self):
        return self.native.Height
