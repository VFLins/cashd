from sys import platform
from copy import copy
from typing import Type, Literal, NewType
import subprocess

if platform == "win32":
    import clr

    clr.AddReference("System.Windows.Forms")
    from System.Windows.Forms import HorizontalAlignment as h_align

from toga.colors import TRANSPARENT
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets.base import Widget
from toga.widgets.table import Table
from toga import (
    TextInput,
    Selection,
    NumberInput,
    Button,
    Box,
)

from cashd import const


def set_col_alignments(table: Table, alignments: list[Literal["l", "c", "r"]]):
    """Set alignment for columns of `table`, the first item in `alignments` will
    apply alignment to the first column, and so on.

    On windows, the first column will always align to the left.
    """
    native_table = table._impl.native
    match platform:
        case "win32":
            align_map = {"l": h_align.Left, "c": h_align.Center, "r": h_align.Right}
            for i, al in enumerate(alignments):
                native_table.Columns[i].TextAlign = align_map[al]
        case "linux":
            native_table = native_table.get_child()
            align_map = {"l": 0.0, "c": 0.5, "r": 1.0}
            for i, al in enumerate(alignments):
                # Align heading
                column = native_table.get_column(i)
                column.set_alignment(align_map[al])
                # Toga-GTK cells include [Gtk.CellRendererPixbuf, Gtk.CellRendererText]
                # Setting alignment only to the text renderer
                cell_text = column.get_cells()[1]
                cell_text.set_property("xalign", align_map[al])
            # Redraw table with new alignment
            native_table.queue_draw()
        case _:
            print(f"Cannot set table alignment on {platform=}")


def form_options_container(children, alignment="end") -> Box:
    """
    Return a `toga.Box` containing elements that shoud be displayed under a form.

    :param children: Widgets that will be contained in this `toga.Box`, usually buttons.
    :param alignment: Horizontal alignment of elements.
    """
    inner_container = Box(style=ROW_OF_BUTTONS, children=children)
    outer_container = Box(
        style=Pack(direction="column", align_items=alignment, width=const.FORM_WIDTH),
        children=[inner_container],
    )
    return outer_container


def user_input(widget_type: Type[Widget]) -> Pack:
    """Returns the default style for the user input's form element."""
    if widget_type in [TextInput, Button]:
        return Pack(margin=(0, 5), width=160, font_size=const.FONT_SIZE)
    elif widget_type is NumberInput:
        return _system_based_number_input_style()
    elif widget_type is Selection:
        return Pack(margin=(0, 5), width=110, font_size=const.FONT_SIZE)
    else:
        return Pack()


def input_annotation(annotation_type: Literal["label", "legend"] = "label") -> Pack:
    """Returns the default style for the user input's annotation element."""
    if annotation_type == "label":
        return _system_based_input_label_style()
    elif annotation_type == "legend":
        return _system_based_input_legend_style()
    else:
        raise ValueError(f"{annotation_type=}, expected one of 'label', 'legend'.")


def number_input_width():
    min_width = 135
    if platform != "linux":
        return const.FONT_SIZE * 7
    width = const.FONT_SIZE * 11
    if width <= min_width:
        return min_width
    else:
        return width


def selection_width():
    if platform == "linux":
        return const.FONT_SIZE * 14
    return const.FONT_SIZE * 12


BUTTON_STYLE = Pack(width=120, margin=(30, 20), font_size=const.FONT_SIZE)
SMALL_BUTTON = Pack(
    font_size=const.FONT_SIZE - 2, margin=(5, 5, 5, 0), width=68, height=24
)
ROW_OF_BUTTONS = Pack(
    direction=ROW,
    align_items="center",
)
VERTICAL_BOX = Pack(
    direction=COLUMN,
    align_items="center",
)
FILLING_VERTICAL_BOX = Pack(
    direction=COLUMN,
    align_items="center",
    flex=1,
)
HORIZONTAL_BOX = Pack(
    direction=ROW,
    width=const.CONTENT_WIDTH,
    align_items="center",
    flex=1,
    margin=(10, 0),
    background_color=TRANSPARENT,
)
FULL_CONTENTS = Pack(
    direction=COLUMN,
    align_items="center",
    padding=(0, 0, 20, 0),
)
PAGE_BODY = Pack(
    flex=1,
    width=const.CONTENT_WIDTH + 10,
    direction=COLUMN,
    align_items="center",
)
TABLE_OF_DATA = Pack(
    flex=1, font_size=const.FONT_SIZE, width=const.FORM_WIDTH, align_items="start"
)
INLINE_LABEL = Pack(font_size=const.FONT_SIZE, padding=15)
GENERIC_LABEL = Pack(
    width=const.CONTENT_WIDTH,
    align_items="start",
    font_size=const.SMALL_FONT_SIZE,
    margin=(0, 0, 22, 0),
)
SHORT_FIELD = Pack(margin=8, width=180, font_size=const.FONT_SIZE)
VERTICAL_ALIGNED_BUTTON = Pack(font_size=const.FONT_SIZE, flex=1, margin=(5, 10))
HORIZONTAL_ALIGNED_BUTTON = Pack(
    margin=(5, 10, 10, 0), width=120, font_size=const.FONT_SIZE
)
BIG_BUTTON = Pack(
    margin=10,
    width=const.FONT_SIZE * 3,
    height=const.FONT_SIZE * 3,
    font_size=const.FONT_SIZE,
)
CONTEXT_BUTTON = Pack(
    font_size=const.FONT_SIZE,
    padding=(20, 0, 10, 5),
    width=90,
)
SEPARATOR = Pack(width=const.CONTENT_WIDTH, margin=5)
HEADING = Pack(
    font_size=const.BIG_FONT_SIZE,
    font_weight="bold",
    width=const.CONTENT_WIDTH,
    padding=(20, 5, 5, 0),
)
WIDE_SELECTION = Pack(margin=(0, 5), width=210, font_size=const.FONT_SIZE)


def _system_based_input_label_style() -> Pack:
    """OS based style for a `toga.Label` element used as label to an input field."""
    if platform == "linux":
        return Pack(margin=(20, 5, 9, 8), width=190, font_size=const.FONT_SIZE)
    else:
        return Pack(margin=(25, 5, 9, 2), width=190, font_size=const.FONT_SIZE)


def _system_based_input_legend_style() -> Pack:
    if platform == "linux":
        return Pack(font_size=const.SMALL_FONT_SIZE, margin=(6, 0, 10, 8), color="gray")
    else:
        return Pack(font_size=const.SMALL_FONT_SIZE, margin=(6, 0, 10, 3), color="gray")


def _system_based_number_input_style() -> Pack:
    """OS based style for a `toga.NumberInput` element used as form input field."""
    if platform == "linux":
        return Pack(
            margin=(0, 5), width=number_input_width(), font_size=const.FONT_SIZE
        )
    else:
        return Pack(
            margin=(0, 5), width=number_input_width(), font_size=const.FONT_SIZE
        )
