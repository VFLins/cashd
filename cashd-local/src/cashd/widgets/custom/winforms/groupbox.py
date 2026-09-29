from __future__ import annotations

import System.Windows.Forms as WinForms
import System.Drawing as Drawing

from toga.handlers import WeakrefCallable
from toga_winforms.container import Container
from toga_winforms.widgets.base import Widget


class GroupBoxImpl(Widget):
    """GroupBox implementation on WinForms."""

    def create(self):
        self.native = WinForms.GroupBox()
        self._content_container = Container(self.native)

        # The checkbox always exists, only its visibility changes, so that it can be
        # shown or hidden whenever ``on_change`` is set or cleared.
        self._checkbox_visible = False
        self._checkbox = WinForms.CheckBox()
        self._checkbox.AutoSize = True
        self._checkbox.Visible = False
        self._checkbox.CheckedChanged += WeakrefCallable(self.checked_changed)
        self.native.Controls.Add(self._checkbox)

        self._update_title()
        self._insets = self._measure_insets()

    def set_title(self, title: str | None):
        self._update_title()

    def set_checkbox_visible(self, visible: bool):
        if visible == self._checkbox_visible:
            return
        self._checkbox_visible = visible
        self._checkbox.Visible = visible
        self._update_title()
        self.interface.refresh()

    def get_value(self) -> bool | None:
        if not self._checkbox_visible:
            return None
        return self._checkbox.Checked

    def set_value(self, value: bool):
        if self._checkbox_visible:
            self._checkbox.Checked = value

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

        if self._checkbox_visible:
            preferred = self._checkbox.PreferredSize
            self._checkbox.Location = Drawing.Point(bounds.X, 0)
            self._checkbox.Size = Drawing.Size(preferred.Width, preferred.Height)
            self._checkbox.BringToFront()

    def checked_changed(self, sender, event):
        self.interface.on_change()

    def _update_title(self):
        if self._checkbox_visible:
            self.native.Text = ""
            self._checkbox.Text = self.title
        else:
            self.native.Text = self.title

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
