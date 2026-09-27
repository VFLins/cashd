from __future__ import annotations
from collections.abc import Iterable

import toga
from toga.style import Pack, TogaApplicator


class GroupBox(toga.Widget):
    _MIN_WIDTH = 0
    _MIN_HEIGHT = 0

    def __init__(
        self,
        title: str | None = None,
        checkbox: bool = False,
        children: Iterable[toga.Widget] | None = None,
        id: str | None = None,
        style: Pack | None = None,
        **kwargs,
    ):
        """Container with border and optional title and checkbox.

        :param title: Title of the container.
        :param checkbox: Tells if the title should include a checkbox.
        :param children: An optional list of children to add to the box.
        :param id: The ID for the widget.
        :param style: A style object, if no style is passed, a default style is passed
          to the GroupBox.
        :param kwargs: Initial style properties.
        """
        self._checkbox = checkbox # needs to be set before toga.Widget.__init__
        super().__init__(
            id=id,
            style=style,
            **kwargs,
        )

        self.title = title

        self._children = []
        if children is not None:
            self.add(*children)

    def _create(self):
        backend = toga.backend

        if backend == "toga_gtk":
            from .gtk.groupbox import GroupBoxImpl
            return GroupBoxImpl(interface=self)

        if backend == "toga_winforms":
            from .winforms.groupbox import GroupBoxImpl
            return GroupBoxImpl(interface=self)

        raise NotImplementedError(f"No GroupBox implementation for backend: {backend}")

    @property
    def title(self) -> str | None:
        return getattr(self, "_title", None)

    @title.setter
    def title(self, title: str | None):
        self._title = title
        self._impl.set_title(title)

    @property
    def value(self) -> bool | None:
        if not self._checkbox:
            return None
        return self._impl.get_value()

    @value.setter
    def value(self, value: bool | None):
        if self.value is None or value is None:
            return
        self._impl.set_value(bool(value))

    @property
    def checkbox(self) -> bool:
        return self._checkbox
