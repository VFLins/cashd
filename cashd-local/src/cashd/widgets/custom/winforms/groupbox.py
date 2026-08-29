from toga_winforms.widgets.box import Box
from toga_winforms.libs import WinForms

class GroupBoxWinForms(Box):
    def create(self):
        # Cria o GroupBox nativo do WinForms
        self.native = WinForms.GroupBox()
        self.native.Text = self.interface.title

    def set_title(self, title):
        self.native.Text = title
