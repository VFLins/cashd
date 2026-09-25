import System.Windows.Forms as WinForms


def create(box_interface, title):
    """Migra os controles do Panel padrão para um GroupBox do WinForms."""
    backend_view = box_interface._impl.native

    if hasattr(backend_view, "Controls"):
        groupbox = WinForms.GroupBox()
        groupbox.Text = title

        groupbox.Size = backend_view.Size
        groupbox.Dock = backend_view.Dock

        while backend_view.Controls.Count > 0:
            control = backend_view.Controls[0]
            backend_view.Controls.Remove(control)
            groupbox.Controls.Add(control)

        box_interface._impl.native = groupbox
