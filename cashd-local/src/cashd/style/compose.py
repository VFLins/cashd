from toga import Widget
from toga.style.pack import ROW, COLUMN, CENTER, LEFT, RIGHT, TOP, BOTTOM, Pack
from toga.widgets.box import Box, Column, Row

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
    def __init__(self, n: int = 1, direction: str = COLUMN, *stylers: Styler):
        self.n = max(1, n)
        self.direction = direction
        self.stylers = stylers

    def arrange(self, children: list, *child_stylers: Styler) -> list[Box]:
        """Ponto de entrada que delega para a função privada correspondente."""
        if self.direction == COLUMN:
            return self._arrange_columns(children, *child_stylers)
        return self._arrange_rows(children, *child_stylers)

    def _get_block_style(self, *external_stylers: Styler) -> Pack:
        block_kw = parent_kw(*self.stylers)
        inherit_kw = child_kw(*external_stylers)
        inherit_kw.update(block_kw)
        return Pack(**inherit_kw)

    def _arrange_columns(self, children: list[Widget], *child_stylers) -> list[Box]:
        """Cria N colunas verticais e distribui os filhos alternadamente (round-robin)."""
        col_style = self._get_block_style(*child_stylers)
        columns = [Column(style=col_style) for _ in range(self.n)]

        style_kw = child_kw(*self.stylers)
        for i, child in enumerate(children):
            child.style = Pack(**style_kw)
            col_index = i % self.n
            columns[col_index].add(child)
        return columns

    def _arrange_rows(self, children: list[Widget], *child_stylers) -> list[Box]:
        """Agrupa os filhos em sub-containers de linha com tamanho máximo N."""
        row_style = self._get_block_style(**child_stylers)
        rows = []

        style_kw = child_kw(*child_stylers)
        for i in range(0, len(children), self.n):
            row_items = children[i : i + self.n]
            row_box = Row(style=row_style)
            for child in row_items:
                child.style = Pack(**style_kw)
                row_box.add(child)

            # Keep last row proportional by adding fillers
            missing_items = self.n - len(row_items)
            for _ in range(missing_items):
                row_box.add(Box(style=Pack(flex=1)))
            rows.append(row_box)
        return rows

# --- 1. Static instances ---

STRETCH = Styler(parent_style={"flex": 1})
CENTER_CONTENT_X = Styler(child_style={"alignment": CENTER})
CENTER_CONTENT_Y = Styler(child_style={"justify_content": CENTER})
CENTER_X = Styler(parent_style={"alignment": CENTER})
CENTER_Y = Styler(parent_style={"justify_content": CENTER})


# --- 2. Customizable instances ---

def COLUMNS(n: int, *stylers: Styler) -> GridHandler:
    """Cria N colunas verticais infinitas e preenche alternadamente."""
    return GridHandler(n, COLUMN, *stylers)

def ROWS(n: int, *stylers: Styler) -> GridHandler:
    """Cria linhas horizontais com no máximo N itens cada."""
    return GridHandler(n, ROW, *stylers)

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
    def __init__(self, *modifiers: Modifier, **kwargs):
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

    def set_modifiers(self, *modifiers: Modifier):
        self._modifiers = [m for m in modifiers if isinstance(m, Modifier)]
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
        child_styler = child_kw(*self.stylers)
        self.style = Pack(**parent_kw(*self.stylers))

        # Delete widgets keeping references
        for child in list(self.children):
            super().remove(child)
        if not self._raw_children:
            return

        # Add widgets from references
        if self.grid_handler is not None:
            containers = self.grid_handler.arrange(self._raw_children, *self.stylers)
            for c in containers:
                super().add(c)
        elif child_styler:
            for child in self._raw_children:
                col_box = Box(style=Pack(**child_styler))
                col_box.add(child)
                super().add(col_box)
        else:
            for child in self._raw_children:
                super().add(child)


def parent_kw(*stylers: Styler) -> dict:
    kw = {}
    for s in stylers:
        s.apply_parent(kw)
    return kw


def child_kw(*stylers: Styler) -> dict:
    kw = {}
    for s in stylers:
        s.apply_child(kw)
    return kw


def get_container(*args, **kwargs) -> ComposedBox:
    return ComposedBox(*args, **kwargs)
