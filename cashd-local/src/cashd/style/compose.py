
from toga.style.pack import ROW, COLUMN, CENTER, LEFT, RIGHT, TOP, BOTTOM
from toga import Box

class Modifier:
    def __init__(self, parent_style: dict = None, child_style: dict = None):
        self.parent_style = parent_style or {}
        self.child_style = child_style or {}

    def apply_parent(self, style_dict: dict):
        style_dict.update(self.parent_style)

    def apply_child(self, style_dict: dict):
        style_dict.update(self.child_style)


# --- 1. Static instances ---

TWO_COLUMNS = Modifier(
    parent_style={"direction": ROW},
    child_style={"direction": COLUMN, "flex": 1},
)

H_STRETCH = Modifier(parent_style={"flex": 1})
H_CENTERED_CONTENT = Modifier(child_style={"alignment": CENTER})
V_CENTERED_CONTENT = Modifier(child_style={"justify_content": CENTER})


# --- 2. Customizable instances ---

def GAP(padding_value: int) -> Modifier:
    """Aplica espaçamento interno (padding) nos containers dos filhos."""
    return Modifier(child_style={"padding": padding_value})

def FLEX(value: int) -> Modifier:
    """Aplica um fator de flexibilidade personalizado ao container pai."""
    return Modifier(parent_style={"flex": value})

def N_COLUMNS(count: int) -> Modifier:
    """Permite criar N colunas de largura proporcional."""
    return Modifier(
        parent_style={"direction": ROW},
        child_style={"direction": COLUMN, "flex": 1},
    )


class ComposedBox(Box):
    def __init__(self, *modifiers, **kwargs):
        self.modifiers = [m for m in modifiers if isinstance(m, Modifier)]

        parent_style = {}
        for mod in self.modifiers:
            mod.apply_parent(parent_style)

        super().__init__(style=Pack(**parent_style), **kwargs)

    def add(self, *children):
        if not children:
            return

        child_style = {}
        for mod in self.modifiers:
            mod.apply_child(child_style)

        if child_style:
            for child in children:
                col_box = toga.Box(style=Pack(**child_style))
                col_box.add(child)
                super().add(col_box)
        else:
            super().add(*children)


def get_container(*args, **kwargs) -> ComposedBox:
    return ComposedBox(*args, **kwargs)
