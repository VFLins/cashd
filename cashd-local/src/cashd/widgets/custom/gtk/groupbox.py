from toga_gtk.widgets.box import Box
from toga_gtk.libs import Gtk

class GroupBoxGTK(Box):
    def create(self):
        # Cria o GtkFrame nativo
        self.native = Gtk.Frame()
        self.native.set_label(self.interface.title)

        # O GtkFrame precisa de um container interno (Gtk.Box) para seus filhos
        self.container_native = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.native.add(self.container_native)

    def set_title(self, title):
        self.native.set_label(title)
