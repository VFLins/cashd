from __future__ import annotations

import locale
from datetime import date, datetime

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402
from travertino.size import at_least  # noqa: E402

from toga_gtk.widgets.base import Widget  # noqa: E402

MIN_DATE = date(1800, 1, 1)
MAX_DATE = date(8999, 12, 31)


def _display_format() -> str:
    """Short date format based on Locale with 4 digit year."""
    try:
        fmt = locale.nl_langinfo(locale.D_FMT)
    except (AttributeError, ValueError):
        fmt = "%Y-%m-%d"
    return fmt.replace("%y", "%Y")


class DateInput(Widget):
    def create(self):
        self._min = MIN_DATE
        self._max = MAX_DATE
        self._value = date.today()
        self._syncing = False  # True when updating by code
        self._clicking = False  # True on user interaction
        self._fmt = _display_format()

        # Entry and button visually linked
        self.native = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.native.get_style_context().add_class("linked")

        self.entry = Gtk.Entry()
        self.entry.set_width_chars(len(date(2000, 12, 28).strftime(self._fmt)) + 1)
        self.entry.connect("activate", self.gtk_entry_activate)
        self.entry.connect("focus-out-event", self.gtk_entry_focus_out)
        self.entry.connect("key-press-event", self.gtk_entry_key_press)

        # --- Calendar
        # Replaced native header to separate behavior when a date is clicked from
        # when navigating the calendar, since both trigger "day_selected".
        self.calendar = Gtk.Calendar()
        self.calendar.set_property("show-heading", False)
        self.calendar.set_property("no-month-change", True)
        self.calendar.connect("day-selected", self.gtk_day_selected)
        self.calendar.connect("button-press-event", self.gtk_calendar_press)
        self.calendar.connect("button-release-event", self.gtk_calendar_release)

        self.prev_button = Gtk.Button.new_from_icon_name(
            "go-previous-symbolic", Gtk.IconSize.BUTTON
        )
        self.next_button = Gtk.Button.new_from_icon_name(
            "go-next-symbolic", Gtk.IconSize.BUTTON
        )
        for button, delta in ((self.prev_button, -1), (self.next_button, 1)):
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.connect("clicked", self.gtk_navigate, delta)
        self.title = Gtk.Label()

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header.pack_start(self.prev_button, False, False, 0)
        header.pack_start(self.title, True, True, 0)
        header.pack_start(self.next_button, False, False, 0)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        content.pack_start(header, False, False, 0)
        content.pack_start(self.calendar, False, False, 0)
        content.show_all()

        self.popover = Gtk.Popover()
        self.popover.set_border_width(6)
        self.popover.add(content)
        self.popover.connect("show", self.gtk_popover_show)

        self.button = Gtk.MenuButton()
        self.button.add(
            Gtk.Image.new_from_icon_name(
                "x-office-calendar-symbolic", Gtk.IconSize.BUTTON
            )
        )
        self.button.set_popover(self.popover)

        self.native.pack_start(self.entry, True, True, 0)
        self.native.pack_start(self.button, False, False, 0)
        self.native.show_all()

        self._sync_ui()

    def _notify(self):
        handler = getattr(self.interface, "_value_changed", None)
        if handler is not None:
            handler()
        else:
            self.interface.on_change()

    def _show_month(self, year: int, month0: int):
        """Mostra um mês no calendário, sem alterar o valor do widget."""
        self._syncing = True
        try:
            self.calendar.select_month(month0, year)
            if (year, month0 + 1) == (self._value.year, self._value.month):
                self.calendar.select_day(self._value.day)
            else:
                self.calendar.select_day(0)  # 0 = sem seleção
        finally:
            self._syncing = False

        self.title.set_text(date(year, month0 + 1, 1).strftime("%B %Y").capitalize())
        index = year * 12 + month0
        self.prev_button.set_sensitive(
            index > self._min.year * 12 + self._min.month - 1
        )
        self.next_button.set_sensitive(
            index < self._max.year * 12 + self._max.month - 1
        )

    def _sync_ui(self):
        self.entry.set_text(self._value.strftime(self._fmt))
        self._show_month(self._value.year, self._value.month - 1)

    def _commit(self, new_value: date):
        new_value = min(max(new_value, self._min), self._max)
        changed = new_value != self._value
        self._value = new_value
        self._sync_ui()
        if changed:
            self._notify()

    def _shift_days(self, delta: int):
        try:
            self._commit(date.fromordinal(self._value.toordinal() + delta))
        except (ValueError, OverflowError):
            pass

    def _commit_text(self):
        try:
            parsed = datetime.strptime(self.entry.get_text().strip(), self._fmt).date()
        except ValueError:
            self._sync_ui()  # Restores original text if typed value is invalid
        else:
            self._commit(parsed)

    def gtk_entry_activate(self, entry):
        self._commit_text()

    def gtk_entry_focus_out(self, entry, event):
        self._commit_text()
        return False

    def gtk_entry_key_press(self, entry, event):
        step = {Gdk.KEY_Up: 1, Gdk.KEY_Down: -1}.get(event.keyval)
        if step is None:
            return False
        self._shift_days(step)  # Update date with Up/Down arrow keys
        return True

    def gtk_popover_show(self, popover):
        self._show_month(self._value.year, self._value.month - 1)

    def gtk_navigate(self, button, delta):
        year, month0, _ = self.calendar.get_date()
        year, month0 = divmod(year * 12 + month0 + delta, 12)
        self._show_month(year, month0)

    def gtk_calendar_press(self, calendar, event):
        # Gtk.Calendar emits "day-selected" right after this handler.
        self._clicking = True
        return False

    def gtk_calendar_release(self, calendar, event):
        GLib.idle_add(self._end_click)
        return False

    def _end_click(self):
        self._clicking = False
        return GLib.SOURCE_REMOVE

    def gtk_day_selected(self, calendar):
        if self._syncing:
            return
        year, month0, day = calendar.get_date()
        if day == 0:
            return
        try:
            new_value = date(year, month0 + 1, day)
        except ValueError:
            return

        from_click = self._clicking
        self._commit(new_value)
        if from_click:
            self.popover.popdown()  # closes when a date is clicked

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._commit(value)

    def get_min_date(self):
        return self._min

    def set_min_date(self, value):
        self._min = value if value is not None else MIN_DATE
        self._commit(self._value)

    def get_max_date(self):
        return self._max

    def set_max_date(self, value):
        self._max = value if value is not None else MAX_DATE
        self._commit(self._value)

    def focus(self):
        self.entry.grab_focus()

    def rehint(self):
        _, natural = self.native.get_preferred_size()
        self.interface.intrinsic.width = at_least(natural.width)
        self.interface.intrinsic.height = natural.height
