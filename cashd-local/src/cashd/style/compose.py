from typing import Any, Generator, Iterable
from toga import Widget
from toga.style.pack import (
    ROW,
    COLUMN,
    CENTER,
    LEFT,
    RIGHT,
    TOP,
    BOTTOM,
    VISIBLE,
    HIDDEN,
    Pack,
)
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
        """Adds the parent style to a style dictionary.

        :param style_dict: Dictionary that receives the parent style values.
        """
        style_dict.update(self.parent_style)

    def apply_child(self, style_dict: dict):
        """Adds the child style to a style dictionary.

        :param style_dict: Dictionary that receives the child style values.
        """
        style_dict.update(self.child_style)

    def reset(self):
        """Resets any internal state, so the next rebuild starts from a clean slate.

        Static stylers hold no state, so this does nothing by default.
        """

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

    def apply_parent(self, style_dict: dict):
        """Adds the next parent style in the cycle to a style dictionary.

        :param style_dict: Dictionary that receives the parent style values.
        """
        kw = next(self.parent_gen)
        style_dict.update(kw)

    def apply_child(self, style_dict: dict):
        """Adds the next child style in the cycle to a style dictionary.

        :param style_dict: Dictionary that receives the child style values.
        """
        kw = next(self.child_gen)
        style_dict.update(kw)

    def reset(self):
        """Restarts both cycles, so the next widget receives the first values again."""
        self.parent_gen = self._get_parent_gen()
        self.child_gen = self._get_child_gen()

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
        """Modifier that distributes the children of a container across N blocks.

        :param n: Number of blocks to create. Values lower than 1 are treated as 1.
        :param direction: Direction of each created block (`ROW` or `COLUMN`).
        :param stylers: Stylers applied to the blocks and to the children placed in them.
        """
        self.n = max(1, n)
        self.direction = direction
        self.stylers = stylers
        self.parent_stylers: Iterable[Styler] = []

    def arrange(self, children: list, *parent_stylers: Styler) -> list[Box]:
        """Entry point that builds the blocks and distributes the children across them.

        :param children: Widgets to be distributed, in order, across the blocks.
        :param parent_stylers: Stylers inherited from the container that owns this handler.
        :return: The blocks, already holding their children and styled.
        """
        self.parent_stylers = parent_stylers
        for s in (*self.parent_stylers, *self.stylers):
            s.reset()
        blocks = []
        for i in range(self.n):
            block = Box(children=self._get_children_at(index=i, children=children))
            # Apply styles inherited from parent block
            apply_styles(as_parent=False, widget=block, stylers=self.parent_stylers)
            # Apply own styles overwriting inherited ones when conflicting
            apply_styles(as_parent=True, widget=block, stylers=self.stylers)
            block.style.direction = self.direction
            blocks.append(block)
        return blocks

    def _get_children_at(self, index: int, children: list[Widget]) -> list[Widget]:
        """Selects the children of block `index` (every N-th widget) and styles each one.

        :param index: Index of the block that will receive the children.
        :param children: All widgets being distributed.
        :return: The widgets that belong to the block.
        """
        subset = children[index :: self.n]
        for child in subset:
            apply_styles(as_parent=False, widget=child, stylers=self.stylers)
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
    """Sets a background color to all of its children."""
    return Styler(child_style={"background_color": color})


def MARGIN(t: int = 0, l: int = 0, b: int = 0, r: int = 0) -> Styler:
    """Sets the margin around the parent widget.

    :param t: Top margin.
    :param l: Left margin.
    :param b: Bottom margin.
    :param r: Right margin.
    """
    # Toga expects the margin tuple as (top, right, bottom, left)
    return Styler(parent_style={"margin": (t, r, b, l)})


def FLEX(value: int) -> Styler:
    """Sets a custom flex factor to the parent widget.

    :param value: Flex factor.
    """
    return Styler(parent_style={"flex": value})


def CONTENT_WIDTH(value: int) -> Styler:
    """Set a common width to all of its children."""
    return Styler(child_style={"width": value})


def WIDTH(value: int) -> Styler:
    """Set a width to the parent widget."""
    return Styler(parent_style={"width": value})


def HEIGHT(value: int) -> Styler:
    """Set a height to the parent widget."""
    return Styler(parent_style={"height": value})


def GAP(value: int) -> Styler:
    """Set spacing around its children."""
    return Styler(parent_style={"gap": value})


# --- 3. Iterable ---


def WIDTHS(*values: int) -> IterableStyler:
    """Cycles through the given widths, applying one to each parent widget."""
    return IterableStyler(parent_style={"width": values})


def CONTENT_WIDTHS(*values: int) -> IterableStyler:
    """Cycles through the given widths, applying one to each child."""
    return IterableStyler(child_style={"width": values})


def FLEXES(*values: int) -> IterableStyler:
    """Cycles through the given flex factors, applying one to each parent widget."""
    return IterableStyler(parent_style={"flex": values})


def CONTENT_FLEXES(*values: int) -> IterableStyler:
    """Cycles through the given flex factors, applying one to each child."""
    return IterableStyler(child_style={"flex": values})


def BG_COLORS(*colors: str) -> IterableStyler:
    """Cycles through the given colors, applying one to each parent widget."""
    return IterableStyler(parent_style={"background_color": colors})


def CONTENT_BG_COLORS(*colors: str) -> IterableStyler:
    """Cycles through the given colors, applying one to each child."""
    return IterableStyler(child_style={"background_color": colors})


# --- 4. Grids ---


def COLUMNS(n: int, *stylers: Styler) -> GridHandler:
    """Creates N vertical columns and fills them alternately.

    :param n: Number of columns.
    :param stylers: Stylers applied to the columns and to their children.
    """
    return GridHandler(n, COLUMN, *stylers)


def ROWS(n: int, *stylers: Styler) -> GridHandler:
    """Creates N horizontal rows and fills them alternately.

    :param n: Number of rows.
    :param stylers: Stylers applied to the rows and to their children.
    """
    return GridHandler(n, ROW, *stylers)


class ComposedBox(Box):
    def __init__(self, *modifiers: Modifier, **kwargs):
        """Box whose layout is described declaratively through modifiers.

        :param modifiers: Modifiers (stylers and at most one grid handler) that
            define the styling and arrangement of this box and its children.
        :param kwargs: Regular `toga.Box` arguments. `children` is kept as the
            list of widgets that the modifiers will arrange.
        """
        raw_children = kwargs.pop("children", [])
        self._raw_children = list(raw_children)
        self._modifiers = [m for m in modifiers if isinstance(m, Modifier)]

        super().__init__(**kwargs)
        self.rebuild()

    def add(self, *children: Widget):
        """Appends widgets to this box and rebuilds its layout.

        :param children: Widgets to be added at the end.
        """
        if not children:
            return
        self._raw_children.extend(children)
        self.rebuild()

    def add_at(self, index: int, *children: Widget):
        """Inserts widgets at a given position and rebuilds the layout.

        :param index: Position where the widgets will be inserted.
        :param children: Widgets to be inserted.
        """
        if not children:
            return
        self._raw_children[index:index] = children
        self.rebuild()

    def remove(self, *children: Widget):
        """Removes widgets from this box and rebuilds its layout.

        :param children: Widgets to be removed. They must be children of this box.
        """
        if not children:
            return
        for child in self._raw_children:
            self._raw_children.remove(child)
        self.rebuild()

    def replace_children(self, *children: Widget):
        """Replaces all current children with the given widgets and rebuilds the
        layout.

        :param children: Widgets that become the only children of this box. Passing
            no widgets leaves the box empty.
        """
        self._raw_children = list(children)
        self.rebuild()

    def set_modifiers(self, *modifiers: Modifier):
        """Replaces the modifiers of this box and rebuilds its layout.

        :param modifiers: New modifiers that define the layout.
        """
        self._modifiers = [m for m in modifiers if isinstance(m, Modifier)]
        self.rebuild()

    @property
    def grid_handler(self) -> GridHandler | None:
        """The grid handler among the modifiers, or `None` when there is none."""
        try:
            return [m for m in self._modifiers if isinstance(m, GridHandler)][0]
        except IndexError:
            return None

    @property
    def stylers(self) -> list[Styler]:
        """The stylers among the modifiers."""
        return [m for m in self._modifiers if isinstance(m, Styler)]

    def rebuild(self):
        """Rebuilds it's layout."""
        # Restart iterable stylers so every rebuild gives the same result
        for s in self.stylers:
            s.reset()

        # Reapply own styling
        apply_styles(as_parent=True, widget=self, stylers=self.stylers)

        # Delete widgets keeping references
        self.style.visibility = HIDDEN
        self.refresh()
        try:
            for child in list(self.children):
                super().remove(child)
            if not self._raw_children:
                return

            # Add widgets from references
            if self.grid_handler is not None:
                containers = self.grid_handler.arrange(
                    self._raw_children, *self.stylers
                )
                for c in containers:
                    super().add(c)
            else:
                for child in self._raw_children:
                    apply_styles(as_parent=False, widget=child, stylers=self.stylers)
                    super().add(child)
        finally:
            # Always restore visibility, even when empty or when an error occurs
            self.style.visibility = VISIBLE


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
    for k, v in kw.items():
        setattr(widget.style, k, v)


def get_container(*args, **kwargs) -> ComposedBox:
    """Shortcut that creates a `ComposedBox`.

    :param args: Modifiers passed on to the `ComposedBox`.
    :param kwargs: Keyword arguments passed on to the `ComposedBox`.
    """
    return ComposedBox(*args, **kwargs)
