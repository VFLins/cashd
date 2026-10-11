from __future__ import annotations

import toga
from toga.platform import get_platform_factory


class Checkbox(toga.Switch):
    def _create(self):
        # ex.: "toga_gtk.factory" -> "toga_gtk"
        backend = get_platform_factory().__name__.split(".")[0]

        if backend == "toga_gtk":
            from .gtk.checkbox import Checkbox as Impl
            return Impl(self)

        return super()._create()


__all__ = ["Checkbox"]
