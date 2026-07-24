
from toga.style.pack import ROW, COLUMN, CENTER, LEFT, RIGHT, TOP, BOTTOM, Pack
from toga import Box, Column, Row

class Modifier:
    """Generic class for the declarative container system."""

class Styler(Modifier):
    def __init__(self, parent_style: dict = None, child_style: dict = None):
        self.parent_style = parent_style or {}
        self.child_style = child_style or {}

    def apply_parent(self, style_dict: dict):
        style_dict.update(self.parent_style)

    def apply_child(self, style_dict: dict):
        style_dict.update(self.child_style)


class GridHandler(Modifier):
    def __init__(self, n: int = 1, direction: str = COLUMN, stretch: bool = False):
        self.n = max(1, n)
        self.direction = direction
        self.stretch = stretch

    def arrange(self, children: list, child_style: dict) -> list[Box]:
        """Ponto de entrada que delega para a função privada correspondente."""
        if self.direction == COLUMN:
            return self._arrange_columns(children, child_style)
        return self._arrange_rows(children, child_style)

    def _arrange_columns(self, children: list, child_style: dict = {}) -> list[Box]:
        """Cria N colunas verticais e distribui os filhos alternadamente (round-robin)."""
        columns = [Column(style=Pack(**child_style)) for _ in range(self.n)]
        if self.stretch:
            for c in columns:
                c.style.flex = 1
                c.style.width = 200

        for i, child in enumerate(children):
            col_index = i % self.n
            columns[col_index].add(child)
        return columns

    def _arrange_rows(self, children: list, child_style: dict = {}) -> list[Box]:
        """Agrupa os filhos em sub-containers de linha com tamanho máximo N."""
        rows = []

        for i in range(0, len(children), self.n):
            row_items = children[i : i + self.n]
            row_box = Row(style=Pack(**self.child_style))
            if self.stretch:
                row_box.style.flex = 1

            for child in row_items:
                row_box.add(child)

            # Keep last row proportional with a filler
            missing_items = self.n - len(row_items)
            for _ in range(missing_items):
                row_box.add(Box(style=Pack(flex=1)))
            rows.append(row_box)
        return rows

# --- 1. Static instances ---

STRETCH = Styler(child_style={"flex": 1})
H_CENTER_CONTENT = Styler(child_style={"alignment": CENTER})
V_CENTER_CONTENT = Styler(child_style={"justify_content": CENTER})
H_CENTER = Styler(parent_style={"alignment": CENTER})
V_CENTER = Styler(parent_style={"justify_content": CENTER})


# --- 2. Customizable instances ---

def N_COLUMNS(count: int, stretch: bool = False) -> GridHandler:
    """Cria N colunas verticais infinitas e preenche alternadamente."""
    return GridHandler(n=count, direction=COLUMN, stretch=stretch)

def N_ROWS(count: int, stretch: bool = False) -> GridHandler:
    """Cria linhas horizontais com no máximo N itens cada."""
    return GridHandler(n=count, direction=ROW, stretch=stretch)

def BG_COLOR(color: str) -> Styler:
    """Sets a background color to the parent widget."""
    return Styler(parent_style={"background_color": color})

def GAP(padding_value: int) -> Styler:
    """Aplica espaçamento interno (padding) nos containers dos filhos."""
    return Styler(child_style={"margin": padding_value})

def H_GAP(value: int) -> Styler:
    """Aplica espaçamento interno (padding) nos containers dos filhos."""
    return Styler(child_style={"margin": (0, value)})

def FLEX(value: int) -> Styler:
    """Aplica um fator de flexibilidade personalizado ao container pai."""
    return Styler(parent_style={"flex": value})

def CONTENT_WIDTH(value: int) -> Styler:
    """Set a common width to all of it's immediate children."""
    return Styler(child_style={"width": value})

def WIDTH(value: int) -> Styler:
    """Set a common width to all of it's immediate children."""
    return Styler(parent_style={"width": value})


class ComposedBox(Box):
    def __init__(self, *modifiers, **kwargs):
        raw_children = kwargs.pop("children", [])
        self._raw_children = list(raw_children)
        self._modifiers = [m for m in modifiers if isinstance(m, Modifier)]

        super().__init__(**kwargs)
        self.rebuild()

    def add(self, *children):
        if not children:
            return
        self._raw_children.extend(children)
        self.rebuild()

    def add_mods(self, *modifiers):
        for m in modifiers:
            if isinstance(m, Styler) and m not in self._modifiers:
                self._modifiers.append(m)
        self.rebuild()

    def rm_mods(self, *modifiers):
        for m in modifiers:
            if m in self._modifiers:
                self._modifiers.remove(m)
        self.rebuild()

    @property
    def grid_handler(self) -> GridHandler | None:
        try:
            return [m for m in self._modifiers if isinstance(m, GridHandler)][0]
        except IndexError:
            return None

    @property
    def stylers(self) -> list[Styler]:
        return [m for m in self._modifiers if isinstance(m, Styler)]

    def rebuild(self):
        """Reconstrói o layout delegando a montagem ao GridHandler se presente."""
        parent_style = {}
        child_style = {}

        # Reset style modifiers
        for mod in self.stylers:
            mod.apply_parent(parent_style)
            mod.apply_child(child_style)
        self.style = Pack(**parent_style)

        # Delete widgets keeping references
        for child in list(self.children):
            super().remove(child)
        if not self._raw_children:
            return

        # Add widgets from references
        if self.grid_handler is not None:
            sub_containers = self.grid_handler.arrange(
                self._raw_children, child_style=child_style
            )
            for sub in sub_containers:
                super().add(sub)
        elif child_style:
            for child in self._raw_children:
                col_box = Box(style=Pack(**child_style))
                col_box.add(child)
                super().add(col_box)
        else:
            for child in self._raw_children:
                super().add(child)


def get_container(*args, **kwargs) -> ComposedBox:
    return ComposedBox(*args, **kwargs)
