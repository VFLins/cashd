from __future__ import annotations

from toga_gtk.libs import Gtk
from toga_gtk.widgets.base import Widget


class GroupBoxImpl(Widget):
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
        top = self._label_height()
        pad = 6
        super().set_bounds(
            x - pad,
            y - top,
            width + 2 * pad,
            height + top + pad,
        )

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

    def _label_height(self):
        label = self.native.get_label_widget()
        if label is None:
            return 0
        return label.get_preferred_height()[0]

    @property
    def title(self):
        return "" if self.interface.title is None else self.interface.title
