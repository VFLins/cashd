from __future__ import annotations

from toga_gtk.container import TogaContainer
from toga_gtk.libs import GTK_VERSION, Gtk
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

        self._content_container = TogaContainer()
        self._content_container._content = self

        if GTK_VERSION < (4, 0, 0):
            self.native.add(self._content_container)
        else:
            self.native.set_child(self._content_container)

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

    def rehint(self):
        if GTK_VERSION < (4, 0, 0):
            width = self.native.get_preferred_width()
            height = self.native.get_preferred_height()
            self.interface.intrinsic.width = width[0]
            self.interface.intrinsic.height = height[0]

        else:
            min_size, _ = self.native.get_preferred_size()
            self.interface.intrinsic.width = min_size.width
            self.interface.intrinsic.height = min_size.height

    @property
    def title(self):
        return "" if self.interface.title is None else self.interface.title

