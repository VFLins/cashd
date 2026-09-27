from __future__ import annotations

import System.Windows.Forms as WinForms
import System.Drawing as Drawing

import toga
from toga_winforms.container import Container
from toga_winforms.widgets.base import Widget


class GroupBoxImpl(Widget):
    """GroupBox implementation on WinForms."""

    _BORDER_CLEARANCE = 30
    """Extra size added to the native GroupBox to keep its border clear of children."""

    def create(self):
        self.native = WinForms.GroupBox()
        self._content_container = Container(self.native)

        if self.interface.checkbox:
            self._title_checkbox = WinForms.CheckBox()
            self._title_checkbox.Text = self.title
            self._title_checkbox.AutoSize = True
            self.native.Controls.Add(self._title_checkbox)
        else:
            self.native.Text = self.title

    def set_title(self, title: str | None):
        title = "" if title is None else title
        if self._title_checkbox is not None:
            self._title_checkbox.Text = title
        else:
            self.native.Text = title

    def get_value(self) -> bool | None:
        if self._title_checkbox is None:
            return None
        return self._title_checkbox.Checked

    def set_value(self, value: bool):
        if self._title_checkbox is not None:
            self._title_checkbox.Checked = value

    def add_child(self, child):
        child.container = self._content_container

    def insert_child(self, index, child):
        self.add_child(child)

    def remove_child(self, child):
        child.container = None

    def rehint(self):
        return

    def set_bounds(self, x, y, width, height):
        grow = self._BORDER_CLEARANCE
        shift = grow / 2
        super().set_bounds(
            x - shift,
            y - shift,
            width + grow,
            height + grow,
        )
        bounds = self.native.DisplayRectangle
        self._content_container.native_content.Location = bounds.Location
        self._content_container.native_content.Size = bounds.Size
        self._content_container.native_content.BackColor = Drawing.Color.Transparent

        if self._title_checkbox is not None:
            preferred = self._title_checkbox.PreferredSize
            self._title_checkbox.Location = Drawing.Point(bounds.X, 0)
            self._title_checkbox.Size = Drawing.Size(preferred.Width, preferred.Height)
            self._title_checkbox.BringToFront()

    @property
    def title(self):
        return "" if self.interface.title is None else self.interface.title

