from __future__ import annotations

import System.Windows.Forms as WinForms
import System.Drawing as Drawing

from toga_winforms.container import Container
from toga_winforms.widgets.base import Widget


class GroupBoxImpl(Widget):
    """Implementação WinForms do GroupBox."""

    def create(self):
        self.native = WinForms.GroupBox()
        self._content_container = Container(self.native)
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
        content_inset = self.scale_in(2) # Use toga.Widget DPI scaling
        self._content_container.native_content.Location = Drawing.Point(
            bounds.X + content_inset,
            bounds.Y + content_inset,
        )
        self._content_container.native_content.Size = Drawing.Size(
            max(0, bounds.Width - 2 * content_inset),
            max(0, bounds.Height - 2 * content_inset),
        )
