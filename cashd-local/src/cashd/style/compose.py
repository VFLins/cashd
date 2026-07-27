from typing import Any, Generator
from toga import Widget
from toga.style.pack import ROW, COLUMN, CENTER, LEFT, RIGHT, TOP, BOTTOM, Pack
from toga.widgets.box import Box, Column, Row

class Modifier:
    """Generic class for the declarative container system."""

class Styler(Modifier):
    def __init__(
        self,
        parent_style: dict[str, Any] | None = None,
        child_style: dict[str, Any] | None = None,
    ):
        """Modifier that allows for applying a single style to one or multiple widgets.

        :param parent_style: Style applied to the widget that receives this modifier.
        :param child_style: Style applied to the widget's children, when possible.
        """
        self.parent_style = parent_style or {}
        self.child_style = child_style or {}

    def apply_parent(self, style_dict: dict):
        style_dict.update(self.parent_style)

    def apply_child(self, style_dict: dict):
        style_dict.update(self.child_style)


class IterableStyler(Styler):
    def __init__(
        self,
        parent_style: dict[str, list[Any]] | None = None,
        child_style: dict[str, list[Any]] | None = None,
    ):
        """Modifier that allows for applying a list of styles iteratively to one or
        multiple widgets.

        :param parent_style: Style applied to the widget that receives this modifier.
        :param child_style: Style applied to the widget's children, when possible.
        """
        super().__init__(parent_style, child_style)

    def get_parent_style_at(self, index: int) -> dict:
        return {
            k: v[index % len(v)] if isinstance(v, (list, tuple)) else v
            for k, v in self.parent_style.items()
        }

    def get_child_style_at(self, index: int) -> dict:
        return {
            k: v[index % len(v)] if isinstance(v, (list, tuple)) else v
            for k, v in self.child_style.items()
        }


class GridHandler(Modifier):
    def __init__(self, n: int = 1, direction: str = COLUMN, *stylers: Styler):
        self.n = max(1, n)
        self.direction = direction
        self.stylers = stylers
        self.parent_stylers: list[Styler] = []

    def arrange(self, children: list, *parent_stylers: Styler) -> list[Box]:
        """Ponto de entrada que delega para a função privada correspondente."""
        blocks = []
        for i in range(self.n):
            block_style, child_style = self._get_next_styles()
            block = Box(
                style=block_style,
                children=self._get_children_at(
                    index=i, style=child_style, children=children
                )
            )
            block.style.direction = self.direction
            blocks.append(block)
        return blocks

    def _get_next_styles(self) -> Generator[tuple[Pack, Pack], None, None]:
        """Gerador infinito que fornece (estilo_do_container, estilo_do_filho) a cada iteração."""
        self.block_kw = getattr(self, "block_kw", parent_kw(*self.stylers))
        self.inherit_kw = getattr(self, "inherit_kw", child_kw(*self.parent_stylers))
        self.child_kw = getattr(self, "child_kw", child_kw(*self.stylers))
        while True:
            b_kw = next(self.block_kw)
            b_kw.update(next(self.inherit_kw))
            c_kw = next(self.child_kw)
            yield Pack(**b_kw), Pack(**c_kw)

    def _get_children_at(self, index: int, style: Pack, children: list[Widget]) -> list[Widget]:
        """Seleciona as crianças da coluna `index` (passo N) e aplica o estilo a cada uma."""
        subset = children[index::self.n]
        for child in subset:
            child.style = style
        return subset


# --- 1. Static ---

STRETCH = Styler(parent_style={"flex": 1})
STRETCH_CONTENT = Styler(child_style={"flex": 1})
V = Styler(parent_style={"direction": COLUMN})
H = Styler(parent_style={"direction": ROW})
V_CONTENT = Styler(child_style={"direction": COLUMN})
H_CONTENT = Styler(child_style={"direction": ROW})
CENTER_CONTENT_X = Styler(child_style={"alignment": CENTER})
CENTER_CONTENT_Y = Styler(child_style={"justify_content": CENTER})
CENTER_X = Styler(parent_style={"alignment": CENTER})
CENTER_Y = Styler(parent_style={"justify_content": CENTER})


# --- 2. Customizable ---

def BG_COLOR(color: str) -> Styler:
    """Sets a background color to the parent widget."""
    return Styler(parent_style={"background_color": color})

def MARGIN(t: int = 0, l: int = 0, b: int  = 0, r: int = 0) -> Styler:
    """Aplica espaçamento interno (padding) nos containers dos filhos."""
    return Styler(parent_style={"margin": (t, l, b, r)})

def FLEX(value: int) -> Styler:
    """Aplica um fator de flexibilidade personalizado ao container pai."""
    return Styler(parent_style={"flex": value})

def CONTENT_WIDTH(value: int) -> Styler:
    """Set a common width to all of it's children."""
    return Styler(child_style={"width": value})

def WIDTH(value: int) -> Styler:
    """Set a common width to all of it's children."""
    return Styler(parent_style={"width": value})

def GAP(value: int) -> Styler:
    """Set spacing around it's children."""
    return Styler(parent_style={"gap": value})


# --- 3. Iterable ---

def WIDTHS(*values: int) -> IterableStyler:
    return IterableStyler(key="width", values=values, is_parent=True)

def CONTENT_WIDTHS(*values: int) -> IterableStyler:
    return IterableStyler(key="width", values=values, is_parent=False)

def FLEXES(*values: int) -> IterableStyler:
    return IterableStyler(key="flex", values=values, is_parent=True)

def BG_COLORS(*values: str) -> IterableStyler:
    return IterableStyler(key="background_color", values=values, is_parent=True)


# --- 4. Grids ---

def COLUMNS(n: int, *stylers: Styler) -> GridHandler:
    """Cria N colunas verticais infinitas e preenche alternadamente."""
    return GridHandler(n, COLUMN, *stylers)

def ROWS(n: int, *stylers: Styler) -> GridHandler:
    """Cria linhas horizontais com no máximo N itens cada."""
    return GridHandler(n, ROW, *stylers)


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


def parent_kw(*stylers: Styler) -> Generator[dict, None, None]:
    """Infinite generator of 'parent' styles."""
    for i in count():
        kw = {}
        for s in stylers:
            if isinstance(s, IterableStyler) and s.is_parent:
                kw.update(s.get_style_at(i))
            elif not isinstance(s, IterableStyler):
                s.apply_parent(kw)
        yield kw


def child_kw(*stylers: Styler) -> Generator[dict, None, None]:
    """Infinite generator of 'child' styles."""
    for i in count():
        kw = {}
        for s in stylers:
            if isinstance(s, IterableStyler) and not s.is_parent:
                kw.update(s.get_style_at(i))
            elif not isinstance(s, IterableStyler):
                s.apply_child(kw)
        yield kw


def get_container(*args, **kwargs) -> ComposedBox:
    return ComposedBox(*args, **kwargs)
