from toga_gtk.libs import Gtk

from tests.cashd.probes.base import SimpleProbe


class Checkbox(SimpleProbe):
    native_class = Gtk.CheckButton

    @property
    def text(self):
        return self.native.get_label() or ""

    @property
    def value(self):
        return self.native.get_active()

    def press(self):
        # clicked() é síncrono; emit("activate") só age em widget realizado
        # e com atraso de 250 ms
        self.native.clicked()
