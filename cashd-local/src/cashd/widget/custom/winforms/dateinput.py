from __future__ import annotations

import re

from System.Globalization import CultureInfo
from System.Windows.Forms import DateTimePickerFormat

from toga_winforms.widgets.dateinput import DateInput as _WinFormsDateInput


def _date_format() -> str:
    """Fetch short date format from locale."""
    pattern = CultureInfo.CurrentCulture.DateTimeFormat.ShortDatePattern
    return re.sub(r"y+", "yyyy", pattern)


class DateInput(_WinFormsDateInput):
    def create(self):
        super().create()
        self.native.ShowUpDown = False
        self.native.ShowCheckBox = False
        self.native.Format = DateTimePickerFormat.Custom
        self.native.CustomFormat = _date_format()
