from __future__ import annotations

from toga_gtk.container import TogaContainer
from toga_gtk.libs import GTK_VERSION, Gtk, Gdk
from toga_gtk.widgets.base import Widget


class GroupBoxImpl(Widget):
    """GroupBox implementation in GTK."""

    def create(self):
        self.native = Gtk.Frame()
        self._checkbox = None
        if self.interface.checkbox:
            self._checkbox = Gtk.CheckButton(label=self.title)
            self.native.set_label_widget(self._checkbox)
        elif self.interface.title is not None:
            self.native.set_label(self.title)

    def set_title(self, title: str | None):
        title = "" if title is None else title
        if self._checkbox is not None:
            self._checkbox.set_label(title)
        else:
            self.native.set_label(title)

    def get_value(self) -> bool | None:
        if self._checkbox is None:
            return None
        return self._checkbox.get_active()

    def set_value(self, value: bool):
        if self._checkbox is not None:
            self._checkbox.set_active(value)

    def set_bounds(self, x, y, width, height):
        top = self._label_height()
        pad = 6
        super().set_bounds(
            x - pad,
            y - top,
            width + 2 * pad,
            height + top + pad
        )

    def _label_height(self):
        label = self.native.get_label_widget()
        if label is None:
            return 0
        return label.get_preferred_height()[0]

    @property
    def title(self):
        return "" if self.interface.title is None else self.interface.title

