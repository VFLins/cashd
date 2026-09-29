from __future__ import annotations

from collections.abc import Iterable

import toga
from toga.style import Pack


class GroupBox(toga.Widget):
    _MIN_WIDTH = 0
    _MIN_HEIGHT = 0

    def __init__(
        self,
        title: str | None = None,
        children: Iterable[toga.Widget] | None = None,
        on_change: toga.widgets.base.OnChangeHandler | None = None,
        id: str | None = None,
        style: Pack | None = None,
        **kwargs,
    ):
        """Container with border and optional title and checkbox.

        The checkbox is shown in the title if, and only if, an ``on_change`` handler
        is set. Setting ``on_change`` to ``None`` hides it again.

        :param title: Title of the container.
        :param children: An optional list of children to add to the box.
        :param on_change: The handler to invoke when the value of the checkbox changes.
          If provided, the title will include a checkbox.
        :param id: The ID for the widget.
        :param style: A style object, if no style is passed, a default style is passed
          to the GroupBox.
        :param kwargs: Initial style properties.
        """
        self._has_checkbox = False

        super().__init__(
            id=id,
            style=style,
            **kwargs,
        )

        self.title = title
        self.on_change = on_change

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
        """Title of the GroupBox."""
        return getattr(self, "_title", None)

    @title.setter
    def title(self, title: str | None):
        self._title = title
        self._impl.set_title(title)

    @property
    def checkbox(self) -> bool:
        """Whether the checkbox is currently shown (read-only).

        It is shown when an ``on_change`` handler is set.
        """
        return self._has_checkbox

    @property
    def value(self) -> bool | None:
        """State of the checkbox, or ``None`` if the checkbox isn't shown."""
        if not self._has_checkbox:
            return None
        return self._impl.get_value()

    @value.setter
    def value(self, value: bool | None):
        if not self._has_checkbox or value is None:
            return
        self._impl.set_value(bool(value))

    @property
    def on_change(self):
        """Handler called when this GroupBox's checkbox changes its value.

        Setting a handler shows the checkbox, setting ``None`` hides it.
        """
        return self._on_change

    @on_change.setter
    def on_change(self, handler):
        self._on_change = toga.handlers.wrapped_handler(self, handler)
        self._has_checkbox = handler is not None
        self._impl.set_checkbox_visible(self._has_checkbox)
