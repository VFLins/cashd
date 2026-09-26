from __future__ import annotations

import System.Windows.Forms as WinForms
import System.Drawing as Drawing

import toga
from toga_winforms.container import Container
from toga_winforms.widgets.base import Widget


class GroupBoxImpl(Widget):
    """GroupBox implementation on WinForms."""

    _BORDER_CLEARANCE = 28
    """Extra size added to the native GroupBox to keep its border clear of children."""

    def create(self):
        self.native = WinForms.GroupBox()
        self._content_container = Container(self.native)
        self._title_container = Container(self.native)
        self._title_widget = None

    def set_title(self, title: str | toga.Switch | None):
        # Cleanup switch if present
        if self._title_widget is not None:
            self._title_widget.container = None
            self._title_widget = None

        # Add switch if attributed, or set text normally otherwise
        if isinstance(title, toga.Switch):
            self.native.Text = "" # Use switch's text
            self._title_widget = title
            title.container = self._title_container
        else:
            self.native.Text = "" if title is None else title

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

        # Calculate bounds to the switch if present
        if self._title_widget is not None:
            switch_native = self._title_widget._impl.native
            preferred = switch_native.PreferredSize

            self._title_container.native_content.Location = Drawing.Point(bounds.X, 0)
            self._title_container.native_content.Size = preferred
            self._title_container.native_content.BackColor = self.native.BackColor
            switch_native.Location = Drawing.Point(0, 0)
            switch_native.Size = preferred
