"""GTK3: implementação do Switch do Toga usando Gtk.CheckButton."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402
from travertino.size import at_least  # noqa: E402

from toga_gtk.widgets.base import Widget  # noqa: E402


class Checkbox(Widget):
    def create(self):
        # O texto faz parte do próprio Gtk.CheckButton (label interno).
        self.native = Gtk.CheckButton()
        self.native.connect("toggled", self.gtk_toggled)
        self.native.show()

    # ------------------------------------------------------------------ eventos
    def gtk_toggled(self, widget):
        self.interface.on_change()

    # ------------------------------------------------------- API esperada pelo core
    def get_text(self):
        return self.native.get_label() or ""

    def set_text(self, text):
        self.native.set_label(text)
        self.interface.refresh()

    def get_value(self):
        return self.native.get_active()

    def set_value(self, value):
        self.native.set_active(bool(value))

    def set_font(self, font):
        # A fonte deve ser aplicada ao label interno do CheckButton.
        label = self.native.get_child()
        native_font = getattr(getattr(font, "_impl", font), "native", None)
        if isinstance(label, Gtk.Label) and native_font is not None:
            label.override_font(native_font)

    def rehint(self):
        _, natural = self.native.get_preferred_size()
        self.interface.intrinsic.width = at_least(natural.width)
        self.interface.intrinsic.height = natural.height
