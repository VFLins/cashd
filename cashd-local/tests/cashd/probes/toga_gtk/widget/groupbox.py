from toga_gtk.libs import Gtk

from tests.cashd.probes.base import SimpleProbe
from cashd.widget import GroupBox as Impl


class GroupBox(SimpleProbe):
    native_class = Gtk.Frame

    @property
    def checkbox_visible(self):
        return self.native.get_label_widget() is self.impl._checkbox

    @property
    def title(self):
        if self.checkbox_visible:
            return self.impl._checkbox.get_label()
        label = self.native.get_label()
        return label if label is not None else ""

    @property
    def value(self):
        return self.impl._checkbox.get_active()

    def toggle(self):
        self.impl._checkbox.emit("activate")
