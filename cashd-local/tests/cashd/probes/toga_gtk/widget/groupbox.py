from toga_gtk.libs import Gtk

from tests.cashd.probes.base import SimpleProbe
from cashd.widget import GroupBox


class GroupBoxProbe(SimpleProbe):
    native_class = Gtk.Frame

    def __init__(self):
        super().__init__(widget=GroupBox())

    @property
    def checkbox_visible(self):
        return self.native.get_label_widget() is self.impl._checkbox

    @property
    def title(self):
        if self.checkbox_visible:
            return self.impl._checkbox.get_label()
        return self.native.get_label() or ""

    @property
    def value(self):
        return self.impl._checkbox.get_active()

    def toggle(self):
        self.impl._checkbox.emit("activate")
