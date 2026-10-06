from toga.style.pack import (
    ROW,
    COLUMN,
    START,
    CENTER,
    END,
    LEFT,
    RIGHT,
)

from .styler import Styler, IterableStyler
from .grid import GridHandler


# --- 1. Static ---

STRETCH = Styler(parent_style={"flex": 1})
STRETCH_CONTENT = Styler(child_style={"flex": 1})
V = Styler(parent_style={"direction": COLUMN})
H = Styler(parent_style={"direction": ROW})
V_CONTENT = Styler(child_style={"direction": COLUMN})
H_CONTENT = Styler(child_style={"direction": ROW})
START_CONTENT_ACROSS = Styler(child_style={"align_items": START})
START_CONTENT_ALONG = Styler(child_style={"justify_content": START})
START_ACROSS = Styler(parent_style={"align_items": START})
START_ALONG = Styler(parent_style={"justify_content": START})
CENTER_CONTENT_ACROSS = Styler(child_style={"align_items": CENTER})
CENTER_CONTENT_ALONG = Styler(child_style={"justify_content": CENTER})
CENTER_ACROSS = Styler(parent_style={"align_items": CENTER})
CENTER_ALONG = Styler(parent_style={"justify_content": CENTER})
END_CONTENT_ACROSS = Styler(child_style={"align_items": END})
END_CONTENT_ALONG = Styler(child_style={"justify_content": END})
END_ACROSS = Styler(parent_style={"align_items": END})
END_ALONG = Styler(parent_style={"justify_content": END})


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
