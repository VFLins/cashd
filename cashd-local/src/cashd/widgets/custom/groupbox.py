import toga
from toga.style import Pack

class GroupBox(toga.Box):
    def __init__(self, title="", id=None, style=None, children=None):
        # Inicializa a interface base
        super().__init__(id=id, style=style, children=children)
        self._title = title

        # Seleciona o backend nativo com base no SO
        factory = toga.App.app.factory
        if factory.backend_name == 'gtk':
            from .gtk.groupbox import GroupBoxGTK
            self._impl = GroupBoxGTK(interface=self)
        elif factory.backend_name == 'winforms':
            from .winforms.groupbox import GroupBoxWinForms
            self._impl = GroupBoxWinForms(interface=self)
        else:
            # Fallback para sistemas não suportados (usa a implementação padrão do Box)
            self._impl = factory.Box(interface=self)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        if hasattr(self._impl, 'set_title'):
            self._impl.set_title(value)
