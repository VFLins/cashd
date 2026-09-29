from __future__ import annotations

import System.Windows.Forms as WinForms
import System.Drawing as Drawing

from toga.handlers import WeakrefCallable
from toga_winforms.container import Container
from toga_winforms.widgets.base import Widget


class GroupBoxImpl(Widget):
    """GroupBox implementation on WinForms."""

    _BORDER_CLEARANCE = 30
    """Extra size added to the native GroupBox to keep its border clear of children."""

    def create(self):
        self.native = WinForms.GroupBox()
        self._content_container = Container(self.native)
        self._checkbox = None

        if self.interface.checkbox:
            self._checkbox = WinForms.CheckBox()
            self._checkbox.Text = self.title
            self._checkbox.AutoSize = True
            self._checkbox.CheckedChanged += WeakrefCallable(self.checked_changed)
            self.native.Controls.Add(self._checkbox)
        else:
            self.native.Text = self.title

        self._insets = self._measure_insets()

    def set_title(self, title: str | None):
        title = "" if title is None else title
        if self._checkbox is not None:
            self._checkbox.Text = title
        else:
            self.native.Text = title

    def get_value(self) -> bool | None:
        if self._checkbox is None:
            return None
        return self._checkbox.Checked

    def set_value(self, value: bool):
        if self._checkbox is not None:
            self._updating = True
            self._checkbox.Checked = value
            self._updating = False

    def add_child(self, child):
        child.container = self._content_container

    def insert_child(self, index, child):
        self.add_child(child)

    def remove_child(self, child):
        child.container = None

    def rehint(self):
        return

    def set_bounds(self, x, y, width, height):
        left, top, right, bottom = self._insets
        grow = self._BORDER_CLEARANCE
        shift = grow / 2
        super().set_bounds(
            x - left,
            y - top,
            width + left + right,
            height + top + bottom,
        )
        bounds = self.native.DisplayRectangle
        native_content = self._content_container.native_content
        native_content.Location = bounds.Location
        native_content.Size = bounds.Size

        if self._checkbox is not None:
            preferred = self._checkbox.PreferredSize
            self._checkbox.Location = Drawing.Point(bounds.X, 0)
            self._checkbox.Size = Drawing.Size(preferred.Width, preferred.Height)
            self._checkbox.BringToFront()

    def checked_changed(self, sender, event):
        self.interface.on_change()

    def _measure_insets(self):
        self.native.Size = Drawing.Size(200, 200)
        d = self.native.DisplayRectangle
        left = d.X
        top = d.Y
        right = 200 - (d.X + d.Width)
        bottom = 200 - (d.Y + d.Height)
        return left, top, right, bottom

    @property
    def title(self):
        return "" if self.interface.title is None else self.interface.title

