from __future__ import annotations

import System.Windows.Forms as WinForms

from toga_winforms.container import Container
from toga_winforms.widgets.base import Widget


class GroupBoxImpl(Widget):
    """Implementação WinForms do GroupBox."""

    def create(self):
        self.native = WinForms.GroupBox()

        if self.interface.title is not None:
            self.native.Text = self.interface.title

        # Children belong to the internal container.
        self._content_container = Container(self.native)

    def set_title(self, title):
        if title is None:
            self.native.Text = ""
        else:
            self.native.Text = title

    @property
    def container(self):
        return self._container

    @container.setter
    def container(self, container):
        if self._container is not None:
            self._container.remove_content(self)

        self._container = container

        if container is not None:
            container.add_content(self)

        for child in self.interface.children:
            child._impl.container = self._content_container

        self.refresh()

    def add_child(self, child):
        child.container = self._content_container

    def insert_child(self, index, child):
        child.container = self._content_container

    def remove_child(self, child):
        child.container = None

    def refresh(self):
        self.rehint()

        if self._container is not None:
            self._container.refreshed()

    def rehint(self):
        preferred = self.native.GetPreferredSize(
            WinForms.Size(0, 0)
        )

        self.interface.intrinsic.width = self.scale_out(
            preferred.Width
        )

        self.interface.intrinsic.height = self.scale_out(
            preferred.Height
        )
