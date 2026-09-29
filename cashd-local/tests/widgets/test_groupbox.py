import toga
import pytest
from ..probes import get_probe
from ..probes import GroupBoxProbe
from unittest.mock import Mock
from cashd.widgets.custom import GroupBox


@pytest.fixture
async def widget():
    return GroupBox("Hello")


async def test_title(widget, probe):
    "The title can be changed while no checkbox is shown"
    assert widget.title == "Hello"
    assert probe.title == "Hello"

    widget.title = "A different title"
    await probe.redraw("GroupBox title should be changed")
    assert widget.title == "A different title"
    assert probe.title == "A different title"

    widget.title = None
    await probe.redraw("GroupBox title should be empty")
    assert widget.title is None
    assert probe.title == ""


async def test_no_checkbox_without_handler(widget, probe):
    "The checkbox is not shown when on_change is None"
    assert not widget.checkbox
    assert widget.value is None
    assert not probe.checkbox_visible

    # Setting a value is ignored while the checkbox is hidden
    widget.value = True
    assert widget.value is None


async def test_checkbox_shown_with_handler(widget, probe):
    "Setting on_change shows the checkbox, clearing it hides the checkbox again"
    on_change = Mock()

    widget.on_change = on_change
    await probe.redraw("Checkbox should be shown")
    assert widget.checkbox
    assert probe.checkbox_visible
    assert widget.value is False
    assert probe.title == "Hello"

    widget.on_change = None
    await probe.redraw("Checkbox should be hidden")
    assert not widget.checkbox
    assert not probe.checkbox_visible
    assert widget.value is None
    assert probe.title == "Hello"
    on_change.assert_not_called()


async def test_checkbox_shown_at_creation(main_window, main_window_probe):
    "Passing on_change to the constructor shows the checkbox"
    from .probe import get_probe

    group = GroupBox("Created", on_change=Mock())
    main_window.content = toga.Box(children=[group])
    probe = get_probe(group)
    await probe.redraw("GroupBox with checkbox should be displayed")

    assert group.checkbox
    assert probe.checkbox_visible
    assert group.value is False
    assert probe.title == "Created"


async def test_title_with_checkbox(widget, probe):
    "The title is displayed next to the checkbox"
    widget.on_change = Mock()
    widget.title = "With checkbox"
    await probe.redraw("Title should be changed")
    assert probe.title == "With checkbox"

    widget.title = None
    await probe.redraw("Title should be empty")
    assert probe.title == ""


async def test_value(widget, probe):
    "The value can be changed programmatically, and fires on_change"
    on_change = Mock()
    widget.on_change = on_change

    widget.value = True
    await probe.redraw("Checkbox should be checked")
    assert widget.value is True
    assert probe.value is True
    on_change.assert_called_once_with(widget)

    on_change.reset_mock()
    widget.value = False
    await probe.redraw("Checkbox should be unchecked")
    assert widget.value is False
    assert probe.value is False
    on_change.assert_called_once_with(widget)

    # None is ignored
    on_change.reset_mock()
    widget.value = None
    assert widget.value is False
    on_change.assert_not_called()


async def test_user_toggle(widget, probe):
    "The user clicking on the checkbox changes the value and fires on_change"
    on_change = Mock()
    widget.on_change = on_change

    probe.toggle()
    await probe.redraw("Checkbox should be checked by the user")
    assert widget.value is True
    on_change.assert_called_once_with(widget)

    on_change.reset_mock()
    probe.toggle()
    await probe.redraw("Checkbox should be unchecked by the user")
    assert widget.value is False
    on_change.assert_called_once_with(widget)


async def test_handler_replaced(widget, probe):
    "Replacing the handler keeps the checkbox and calls only the new handler"
    first = Mock()
    second = Mock()

    widget.on_change = first
    widget.on_change = second
    await probe.redraw("Checkbox should still be shown")
    assert probe.checkbox_visible

    probe.toggle()
    await probe.redraw("Checkbox should be toggled")
    first.assert_not_called()
    second.assert_called_once_with(widget)


async def test_children(widget, probe):
    "Children can be added to and removed from the GroupBox"
    child = toga.Button("Inside", style=toga.style.Pack(width=100, height=30))

    widget.add(child)
    await probe.redraw("Child should be displayed inside the GroupBox")
    assert child in widget.children
    assert child.parent is widget

    widget.remove(child)
    await probe.redraw("Child should be removed")
    assert child not in widget.children
    assert child.parent is None
