import System.Windows.Forms as WinForms

from tests.cashd.probes.base import SimpleProbe
from cashd.widgets.custom import GroupBox


class GroupBoxProbe(SimpleProbe):
    native_class = WinForms.GroupBox

    def __init__(self):
        super().__init__(widget=GroupBox())

    @property
    def checkbox_visible(self):
        return bool(self.impl._checkbox.Visible)

    @property
    def title(self):
        if self.checkbox_visible:
            return self.impl._checkbox.Text
        return self.native.Text

    @property
    def value(self):
        return bool(self.impl._checkbox.Checked)

    def toggle(self):
        self.impl._checkbox.PerformClick()
