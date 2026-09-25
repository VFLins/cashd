from __future__ import annotations

import System.Windows.Forms as WinForms
import System.Drawing as Drawing

from toga_winforms.container import Container
from toga_winforms.widgets.base import Widget


class GroupBoxContainer(Container):
    INSET = 85

    def apply_layout(self, layout_width, layout_height):
        super().apply_layout(layout_width, layout_height)
        if self.content is None:
            return

        print(
            "CONTAINER:",
            "panel=",
            self.native_content.Location.X,
            self.native_content.Location.Y,
            self.native_content.Width,
            self.native_content.Height,
            "child=",
            self.content.native.Location.X,
            self.content.native.Location.Y,
            self.content.native.Width,
            self.content.native.Height,
        )

        inset = self.scale_in(self.INSET)
        width = max(0, self.native_width - 2 * inset)
        height = max(0, self.native_height - 2 * inset)

        self.content.native.Location = Drawing.Point(inset, inset)
        self.content.native.Size = Drawing.Size(width, height)

        print(
            "AFTER:",
            self.content.native.Location.X,
            self.content.native.Location.Y,
            self.content.native.Width,
            self.content.native.Height,
        )


class GroupBoxImpl(Widget):
    """Implementação WinForms do GroupBox."""

    def create(self):
        self.native = WinForms.GroupBox()
        self._content_container = GroupBoxContainer(self.native)
        self._ensure_bounds()

    def set_title(self, title: str | None):
        self.native.Text = "" if title is None else title
        self._ensure_bounds()

    def add_child(self, child):
        child.container = self._content_container

    def insert_child(self, index, child):
        self.add_child(child)

    def remove_child(self, child):
        child.container = None

    def rehint(self):
        return
        preferred = self.native.GetPreferredSize(Drawing.Size(0, 0))
        self.interface.intrinsic.width = preferred.Width
        self.interface.intrinsic.height = preferred.Height

    def set_bounds(self, x, y, width, height):
        super().set_bounds(x, y, width, height)
        self._ensure_bounds()

    def _ensure_bounds(self):
        """Handler added to ensure that content is contained inside the borders."""
        bounds = self.native.DisplayRectangle
        self._content_container.native_content.Location = bounds.Location
        self._content_container.native_content.Size = bounds.Size
