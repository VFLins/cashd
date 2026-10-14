from types import SimpleNamespace

from toga_gtk.libs import Gdk, Gtk

from tests.cashd.probes.base import SimpleProbe


class DateInput(SimpleProbe):
    native_class = Gtk.Box

    def __init__(self, widget):
        super().__init__(widget=widget)

    @property
    def text(self):
        return self.impl.entry.get_text()

    def expected_text(self, value):
        """Text displayed by `widget.value` (uses locale)."""
        return value.strftime(self.impl._fmt)

    @property
    def shown_month(self):
        year, month0, _ = self.impl.calendar.get_date()
        return year, month0 + 1

    @property
    def prev_enabled(self):
        return self.impl.prev_button.get_sensitive()

    @property
    def next_enabled(self):
        return self.impl.next_button.get_sensitive()

    @property
    def popover_visible(self):
        return self.impl.popover.get_visible()

    def type_text(self, text):
        # Gtk.Entry has synchronous "activate" (unlike Gtk.Button)
        self.impl.entry.set_text(text)
        self.impl.entry.emit("activate")

    def press_key(self, keyval):
        event = SimpleNamespace(keyval=keyval)
        return self.impl.gtk_entry_key_press(self.impl.entry, event)

    def press_up(self):
        return self.press_key(Gdk.KEY_Up)

    def press_down(self):
        return self.press_key(Gdk.KEY_Down)

    def next_month(self):
        self.impl.next_button.clicked()

    def prev_month(self):
        self.impl.prev_button.clicked()

    def open_popover(self):
        self.impl.popover.popup()

    def click_day(self, day):
        """Simulates the user clicking on a calendar date."""
        self.impl._clicking = True
        try:
            self.impl.calendar.select_day(day)
        finally:
            self.impl._end_click()
