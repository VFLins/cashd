import System.Windows.Forms as WinForms
from tests.cashd.probes.base import SimpleProbe


class GroupBox(SimpleProbe):
    native_class = WinForms.GroupBox

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
        self.impl._checkbox.Checked = not self.impl._checkbox.Checked
