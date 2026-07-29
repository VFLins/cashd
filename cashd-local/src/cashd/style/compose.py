from typing import Any, Generator, Iterable
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

    def __repr__(self):
        _repr = "<Styler"
        if self.parent_style:
            _repr = _repr + f" parent_style={self.parent_style}"
        if self.child_style:
            _repr = _repr + f" child_style={self.child_style}"
        return _repr + ">"


class IterableStyler(Styler):
    def __init__(
        self,
        parent_style: dict[str, Iterable[Any]] | None = None,
        child_style: dict[str, Iterable[Any]] | None = None,
    ):
        """Modifier that allows for applying a list of styles iteratively to one or
        multiple widgets.

        :param parent_style: Style applied to the widget that receives this modifier.
        :param child_style: Style applied to the widget's children, when possible.
        """
        super().__init__(parent_style, child_style)
        self.parent_gen = self._get_parent_gen()
        self.child_gen = self._get_child_gen()

    def apply_parent(style_dict: dict):
        kw = next(self.parent_gen)
        style_dict.update(kw)

    def apply_child(style_dict: dict):
        kw = next(self.child_gen)
        style_dict.update(kw)

    def _get_parent_gen(self) -> Generator[dict, None, None]:
        index = 0
        while True:
            yield {
                k: v[index % len(v)] if isinstance(v, (list, tuple)) else v
                for k, v in self.parent_style.items()
            }
            index = index + 1

    def _get_child_gen(self) -> Generator[dict, None, None]:
        index = 0
        while True:
            yield {
                k: v[index % len(v)] if isinstance(v, (list, tuple)) else v
                for k, v in self.child_style.items()
            }
            index = index + 1


class GridHandler(Modifier):
    def __init__(self, n: int = 1, direction: str = COLUMN, *stylers: Styler):
        self.n = max(1, n)
        self.direction = direction
        self.stylers = stylers
        self.parent_stylers: Iterable[Styler] = []

    def arrange(self, children: list, *parent_stylers: Styler) -> list[Box]:
        """Ponto de entrada que delega para a função privada correspondente."""
        self.parent_stylers = parent_stylers
        blocks = []
        for i in range(self.n):
            block = Box(
                children=self._get_children_at(
                    index=i, style_gen=child_style_gen, children=children
                )
            )
            # Apply styles inherited from parent block
            apply_styles(as_parent=False, block, self.parent_stylers)
            # Apply own styles overwriting inherited ones when conflicting
            apply_styles(as_parent=True, block, self.stylers)
            block.style.direction = self.direction
            blocks.append(block)
        return blocks

    def _get_children_at(self, index: int, children: list[Widget]) -> list[Widget]:
        """Seleciona as crianças da coluna `index` (passo N) e aplica o estilo a cada uma."""
        subset = children[index::self.n]
        for child in subset:
            apply_styles(as_parent=False, child, self.stylers)
        return subset


# --- 1. Static ---

STRETCH = Styler(parent_style={"flex": 1})
STRETCH_CONTENT = Styler(child_style={"flex": 1})
V = Styler(parent_style={"direction": COLUMN})
H = Styler(parent_style={"direction": ROW})
V_CONTENT = Styler(child_style={"direction": COLUMN})
H_CONTENT = Styler(child_style={"direction": ROW})
CENTER_CONTENT_X = Styler(child_style={"align_items": CENTER})
CENTER_CONTENT_Y = Styler(child_style={"justify_content": CENTER})
CENTER_X = Styler(parent_style={"align_items": CENTER})
CENTER_Y = Styler(parent_style={"justify_content": CENTER})


# --- 2. Customizable ---

def BG_COLOR(color: str) -> Styler:
    """Sets a background color to the parent widget."""
    return Styler(parent_style={"background_color": color})

def CONTENT_BG_COLOR(color: str) -> Styler:
    """Sets a background color to the parent widget."""
    return Styler(child_style={"background_color": color})

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
    return IterableStyler(parent_style={"width": values})

def CONTENT_WIDTHS(*values: int) -> IterableStyler:
    return IterableStyler(child_style={"width": values})

def FLEXES(*values: int) -> IterableStyler:
    return IterableStyler(parent_style={"flex": values})

def CONTENT_FLEXES(*values: int) -> IterableStyler:
    return IterableStyler(child_style={"flex": values})

def BG_COLORS(*colors: str) -> IterableStyler:
    return IterableStyler(parent_style={"background_color": colors})

def CONTENT_BG_COLORS(*colors: str) -> IterableStyler:
    return IterableStyler(child_style={"background_color": colors})


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

    def add(self, *children: Widget):
        if not children:
            return
        self._raw_children.extend(children)
        self.rebuild()

    def add_at(self, index: int, *children: Widget):
        if not children:
            return
        self._raw_children[index:index] = children

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
        """Rebuilds it's layout."""
        # Reapply own styling
        apply_styles(as_parent=True, self, self.stylers)

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
        else:
            for child in self._raw_children:
                apply_styles(as_parent=False, child, self.stylers)
                super().add(child)


def apply_styles(as_parent: bool, widget: Widget, stylers: list[Styler]):
    """Apply multiple styles to a Widget without removing widget's non-conflicting
    styles.

    :param as_parent: Boolean indicating if this `widget` should use parent styles.
    :param widget: A `toga.Widget` that will get the styles.
    :param stylers: Stylers holding styles that will be passed on to the widget.
    """
    kw = dict()
    for s in stylers:
        if as_parent:
            s.apply_parent(kw)
        else:
            s.apply_child(kw)
    for k, v in kw.items()
        setattr(widget.style, k, v)


def get_container(*args, **kwargs) -> ComposedBox:
    return ComposedBox(*args, **kwargs)
