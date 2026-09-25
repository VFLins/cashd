from gi.repository import Gtk


def create(box_interface, title):
    """Encapsula a implementação do Toga em um Gtk.Frame."""
    backend_view = box_interface._impl.native

    if isinstance(backend_view, Gtk.Box):
        frame = Gtk.Frame(label=title)

        parent = backend_view.get_parent()
        if parent:
            parent.remove(backend_view)

        frame.add(backend_view)
        box_interface._impl.native = frame
