import toga
import pytest
from ..probes import get_probe
from unittest.mock import Mock
from cashd.widget import GroupBox


@pytest.fixture
async def widget():
    return GroupBox("Hello")


@pytest.fixture(scope="function")
def groupbox_probe():
    probe = get_probe("widgets", "GroupBoxProbe")
    return probe()


async def test_title(widget, groupbox_probe):
    "The title can be changed while no checkbox is shown"
    assert widget.title == "Hello"
    assert groupbox_probe.title == "Hello"

    widget.title = "A different title"
    await groupbox_probe.redraw("GroupBox title should be changed")
    assert widget.title == "A different title"
    assert groupbox_probe.title == "A different title"

    widget.title = None
    await probe.redraw("GroupBox title should be empty")
    assert widget.title is None
    assert groupbox.probe.title == ""


async def test_no_checkbox_without_handler(widget, groupbox_probe):
    "The checkbox is not shown when on_change is None"
    assert not widget.checkbox
    assert widget.value is None
    assert not groupbox_probe.checkbox_visible

    # Setting a value is ignored while the checkbox is hidden
    widget.value = True
    assert widget.value is None


async def test_checkbox_shown_with_handler(widget, groupbox_probe):
    "Setting on_change shows the checkbox, clearing it hides the checkbox again"
    on_change = Mock()

    widget.on_change = on_change
    await groupbox_probe.redraw("Checkbox should be shown")
    assert widget.checkbox
    assert groupbox_probe.checkbox_visible
    assert widget.value is False
    assert groupbox_probe.title == "Hello"

    widget.on_change = None
    await groupbox_probe.redraw("Checkbox should be hidden")
    assert not widget.checkbox
    assert not probe.checkbox_visible
    assert widget.value is None
    assert groupbox_probe.title == "Hello"
    on_change.assert_not_called()


async def test_checkbox_shown_at_creation(
    main_window, groupbox_probe, main_window_probe
):
    "Passing on_change to the constructor shows the checkbox"
    group = GroupBox("Created", on_change=Mock())
    main_window.content = toga.Box(children=[group])
    await groupbox_probe.redraw("GroupBox with checkbox should be displayed")

    assert group.checkbox
    assert groupbox_probe.checkbox_visible
    assert group.value is False
    assert groupbox_probe.title == "Created"


async def test_title_with_checkbox(widget, groupbox_probe):
    "The title is displayed next to the checkbox"
    widget.on_change = Mock()
    widget.title = "With checkbox"
    await groupbox_probe.redraw("Title should be changed")
    assert groupbox_probe.title == "With checkbox"

    widget.title = None
    await probe.redraw("Title should be empty")
    assert groupbox_probe.title == ""


async def test_value(widget, groupbox_probe):
    "The value can be changed programmatically, and fires on_change"
    on_change = Mock()
    widget.on_change = on_change

    widget.value = True
    await groupbox_probe.redraw("Checkbox should be checked")
    assert widget.value is True
    assert groupbox_probe.value is True
    on_change.assert_called_once_with(widget)

    on_change.reset_mock()
    widget.value = False
    await groupbox_probe.redraw("Checkbox should be unchecked")
    assert widget.value is False
    assert groupbox_probe.value is False
    on_change.assert_called_once_with(widget)

    # None is ignored
    on_change.reset_mock()
    widget.value = None
    assert widget.value is False
    on_change.assert_not_called()


async def test_user_toggle(widget, groupbox_probe):
    "The user clicking on the checkbox changes the value and fires on_change"
    on_change = Mock()
    widget.on_change = on_change

    groupbox_probe.toggle()
    await groupbox_probe.redraw("Checkbox should be checked by the user")
    assert widget.value is True
    on_change.assert_called_once_with(widget)

    on_change.reset_mock()
    groupbox_probe.toggle()
    await groupbox_probe.redraw("Checkbox should be unchecked by the user")
    assert widget.value is False
    on_change.assert_called_once_with(widget)


async def test_handler_replaced(widget, groupbox_probe):
    "Replacing the handler keeps the checkbox and calls only the new handler"
    first = Mock()
    second = Mock()

    widget.on_change = first
    widget.on_change = second
    await groupbox_probe.redraw("Checkbox should still be shown")
    assert groupbox_probe.checkbox_visible

    groupbox_probe.toggle()
    await groupbox_probe.redraw("Checkbox should be toggled")
    first.assert_not_called()
    second.assert_called_once_with(widget)


async def test_children(widget, groupbox_probe):
    "Children can be added to and removed from the GroupBox"
    child = toga.Button("Inside", style=toga.style.Pack(width=100, height=30))

    widget.add(child)
    await groupbox_probe.redraw("Child should be displayed inside the GroupBox")
    assert child in widget.children
    assert child.parent is widget

    widget.remove(child)
    await groupbox_probe.redraw("Child should be removed")
    assert child not in widget.children
    assert child.parent is None
