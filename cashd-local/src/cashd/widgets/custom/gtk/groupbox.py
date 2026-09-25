from __future__ import annotations

from toga_gtk.container import TogaContainer
from toga_gtk.libs import GTK_VERSION, Gtk
from toga_gtk.widgets.base import Widget


class GroupBoxImpl(Widget):
    """Implementação GTK do GroupBox."""

    def create(self):
        self.native = Gtk.Frame()

        if self.interface.title is not None:
            self.native.set_label(self.interface.title)

        self._content_container = TogaContainer()
        self._content_container._content = self

        # Insert the content in a Gtk.Frame
        if GTK_VERSION < (4, 0, 0):
            self.native.add(self._content_container)
        else:
            self.native.set_child(self._content_container)

    def set_title(self, title: str | None):
        self.native.set_label(title)

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
