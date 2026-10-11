from __future__ import annotations

from toga_gtk.libs import Gtk, GTK_VERSION
from toga_gtk.libs.styles import get_font_css
from toga_gtk.widgets.base import Widget


class GroupBox(Widget):
    """GroupBox implementation in GTK."""

    def create(self):
        self.native = Gtk.Frame()

        # The checkbox always exists, but is only used as the Frame's label widget
        # while ``on_change`` is set.
        self._checkbox_visible = False
        self._checkbox = Gtk.CheckButton(label=self.title)
        self._checkbox.connect("toggled", self.checked_changed)

        self._update_title()

    def set_title(self, title: str | None):
        self._update_title()

    def set_checkbox_visible(self, visible: bool):
        if visible == self._checkbox_visible:
            return
        self._checkbox_visible = visible
        self._update_title()
        self.interface.refresh()

    def get_value(self) -> bool | None:
        if not self._checkbox_visible:
            return None
        return self._checkbox.get_active()

    def set_value(self, value: bool):
        if self._checkbox_visible:
            self._checkbox.set_active(value)

    def set_bounds(self, x, y, width, height):
        top, right, bottom, left = self.insets
        x = x - left
        y = y - top
        width = width + left + right
        height = height + top + bottom
        super().set_bounds(x, y, width, height)
        a = self.native.get_allocation()

    def checked_changed(self, widget):
        self.interface.on_change()

    def _update_title(self):
        if self._checkbox_visible:
            self._checkbox.set_label(self.title)
            self.native.set_label_widget(self._checkbox)
            self._checkbox.set_visible(True)
        else:
            # Replaces the checkbox (if it was the label widget) with a plain label.
            self.native.set_label(self.title or None)

    @property
    def title(self):
        return "" if self.interface.title is None else self.interface.title

    @property
    def insets(self) -> tuple:
        left, bottom, right, = 6, 6, 6
        label = self.native.get_label_widget()
        top = label.get_preferred_height()[0] if label is not None else 0
        return top, right, bottom, left

