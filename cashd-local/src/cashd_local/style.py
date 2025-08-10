from sys import platform
from copy import copy
from typing import Type, Literal, NewType
import subprocess

from toga.colors import TRANSPARENT
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.widgets.base import Widget
from toga import (
    TextInput,
    Selection,
    NumberInput,
    Button,
    Box,
)

from cashd import const


def write_args(**kwargs):
    # if platform != "linux":
    #    return kwargs
    if "alignment" in kwargs.keys():
        match kwargs["alignment"]:
            case "left":
                kwargs["align_items"] = "start"
            case "right":
                kwargs["align_items"] = "end"
            case "center":
                kwargs["align_items"] = "center"
        del kwargs["alignment"]
    if "padding" in kwargs.keys():
        kwargs["margin"] = copy(kwargs["padding"])
        del kwargs["padding"]
    return kwargs


def form_options_container(children, alignment="end") -> Box:
    """
    Return a `toga.Box` containing elements that shoud be displayed under a form.

    :param children: Widgets that will be contained in this `toga.Box`, usually buttons.
    :param alignment: Horizontal alignment of elements.
    """
    inner_container = Box(style=ROW_OF_BUTTONS, children=children)
    outer_container = Box(
        style=Pack(direction="column", align_items=alignment,
                   width=const.FORM_WIDTH),
        children=[inner_container],
    )
    return outer_container


def user_input(widget_type: Type[Widget]) -> Pack:
    """Returns the default style for the user input's form element."""
    if widget_type in [TextInput, Button]:
        return Pack(margin=(0, 5), width=190, font_size=const.FONT_SIZE)
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
        return Pack(font_size=const.SMALL_FONT_SIZE, margin=(0, 0, 10, 5))
    else:
        raise ValueError(
            f"{annotation_type=}, expected one of 'label', 'legend'.")


def number_input_width():
    if platform != "linux":
        return const.FONT_SIZE * 7
    width = const.FONT_SIZE * 13
    if width <= 160:
        return 160
    else:
        return width


def selection_width():
    if platform == "linux":
        return const.FONT_SIZE * 14
    return const.FONT_SIZE * 12


BUTTON_STYLE = Pack(
    **write_args(width=120, padding=(30, 20), font_size=const.FONT_SIZE)
)
SMALL_BUTTON = Pack(
    font_size=const.FONT_SIZE - 2, margin=(5, 5, 5, 0), width=68, height=24
)
ROW_OF_BUTTONS = Pack(
    direction=ROW,
    align_items="center",
)
VERTICAL_BOX = Pack(
    direction=COLUMN,
    alignment="center",
)
FILLING_VERTICAL_BOX = Pack(
    direction=COLUMN,
    alignment="center",
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
    **write_args(
        direction=COLUMN,
        alignment="center",
        padding=(0, 0, 20, 0),
    )
)
PAGE_BODY = Pack(
    **write_args(
        flex=1,
        width=const.CONTENT_WIDTH + 20,
        direction=COLUMN,
        alignment="center",
    )
)
DATE_INPUT_CONTROLS = Pack(**write_args(direction=ROW, alignment="center"))
TABLE_OF_DATA = Pack(
    flex=1, font_size=const.FONT_SIZE, width=const.CONTENT_WIDTH, align_items="start"
)
INLINE_LABEL = Pack(
    **write_args(
        font_size=const.FONT_SIZE,
        padding=15,
    )
)
GENERIC_LABEL = Pack(
    **write_args(
        width=const.CONTENT_WIDTH,
        alignment="left",
        font_size=const.SMALL_FONT_SIZE,
        padding=(0, 0, 22, 0),
    )
)
SHORT_FIELD = Pack(
    **write_args(
        padding=8,
        width=180,
        font_size=const.FONT_SIZE,
    )
)
VERTICAL_ALIGNED_BUTTON = Pack(
    **write_args(
        font_size=const.FONT_SIZE,
        flex=1,
        padding=(5, 10),
    )
)
HORIZONTAL_ALIGNED_BUTTON = Pack(
    **write_args(padding=(5, 10, 10, 0), width=120, font_size=const.FONT_SIZE)
)
BIG_BUTTON = Pack(
    **write_args(
        margin=10,
        width=const.FONT_SIZE * 3,
        height=const.FONT_SIZE * 3,
        font_size=const.FONT_SIZE,
    )
)
CONTEXT_BUTTON = Pack(
    font_size=const.FONT_SIZE,
    padding=(20, 0, 10, 5),
    width=90,
)
SEPARATOR = Pack(
    **write_args(
        width=const.CONTENT_WIDTH,
        padding=5,
    )
)
WIDE_SELECTION = Pack(
    **write_args(
        padding=(0, 5),
        width=210,
        font_size=const.FONT_SIZE,
    )
)


def _system_based_input_label_style() -> Pack:
    """OS based style for a `toga.Label` element used as label to an input field."""
    if platform == "linux":
        return Pack(margin=(15, 5, 2, 8), width=190, font_size=const.FONT_SIZE)
    else:
        return Pack(margin=(25, 5, 2, 2), width=190, font_size=const.FONT_SIZE)


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
