from __future__ import annotations

import toga
from toga.platform import get_platform_factory


class DateInput(toga.DateInput):
    def _create(self):
        """Import a modified implementation when available, fallback to the original
        otherwise.
        """
        backend = get_platform_factory().__name__.split(".")[0]
        if backend == "toga_winforms":
            from .winforms.dateinput import DateInput as Impl
            return Impl(self)

        if backend == "toga_gtk":
            from .gtk.dateinput import DateInput as Impl
            return Impl(self)

        return super()._create()


__all__ = ["DateInput"]
