import toga
from toga.style.pack import COLUMN


class GroupBoxFactory:
    """Fábrica responsável por mapear e construir as visões de backend do GroupBox."""

    _registry = {
        "toga_gtk": ".gtk.groupbox",
        "toga_winforms": ".winforms.groupbox"
    }

    @classmethod
    def build(cls, box_interface, title):
        backend_name = toga.backend

        if backend_name in cls._registry:
            module_path = cls._registry[backend_name]
            module = importlib.import_module(module_path, package=__name__)
            module.create(box_interface, title)
        else:
            print(f"[Warning] Suporte indisponível para o backend: {backend_name}")


class GroupBox(toga.Box):
    """Componente visível do Toga que agrupa graficamente os elementos filhos."""

    def __init__(self, title, children=None, id=None, style=None):
        super().__init__(id=id, style=style, children=children)
        self.style.direction = COLUMN
        self.title = title

        GroupBoxFactory.build(self, self.title)
