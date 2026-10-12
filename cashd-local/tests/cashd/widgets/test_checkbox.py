from unittest.mock import Mock

import pytest
import pytest_asyncio
import toga

from cashd.widget import Checkbox  # ajuste o caminho do import ao seu projeto

from ..probes import get_probe


def make_probe(widget):
    probe_class = get_probe("widget", "Checkbox")
    return probe_class(widget)


@pytest.fixture
def on_change():
    return Mock()


@pytest_asyncio.fixture
async def widget(mainwindow, on_change):
    old_content = mainwindow.content
    widget = Checkbox("Option", on_change=on_change)
    mainwindow.content = toga.Box(children=[widget])
    on_change.reset_mock()  # ignora eventos disparados na criação
    yield widget
    mainwindow.content = old_content


@pytest.fixture
async def probe(widget):
    return make_probe(widget)


async def test_initial_state(widget, probe):
    "The checkbox shows its text and starts unchecked"
    await probe.redraw("Checkbox should be displayed unchecked")
    assert widget.text == "Option"
    assert probe.text == "Option"
    assert widget.value is False
    assert probe.value is False


async def test_initial_value_true(mainwindow):
    "A checkbox created with value=True starts checked"
    old_content = mainwindow.content
    widget = Checkbox("Checked", value=True)
    mainwindow.content = toga.Box(children=[widget])
    probe = make_probe(widget)
    await probe.redraw("Checkbox should be displayed checked")

    assert widget.value is True
    assert probe.value is True

    mainwindow.content = old_content


async def test_text(widget, probe):
    "The text can be changed"
    widget.text = "Another text"
    await probe.redraw("Checkbox text should change")
    assert widget.text == "Another text"
    assert probe.text == "Another text"


async def test_value_by_code(widget, probe, on_change):
    "Changing the value in code updates the native widget and fires on_change"
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


async def test_same_value_no_event(widget, probe, on_change):
    "Setting the value it already has doesn't fire on_change"
    widget.value = False
    await probe.redraw("Value unchanged")
    on_change.assert_not_called()


async def test_user_press(widget, probe, on_change):
    "A user click toggles the value and fires on_change"
    probe.press()
    await probe.redraw("Checkbox should be checked by the user")
    assert widget.value is True
    on_change.assert_called_once_with(widget)

    on_change.reset_mock()
    probe.press()
    await probe.redraw("Checkbox should be unchecked by the user")
    assert widget.value is False
    on_change.assert_called_once_with(widget)


async def test_toggle_method(widget, probe, on_change):
    "toggle() flips the value"
    widget.toggle()
    await probe.redraw("Checkbox toggled by code")
    assert widget.value is True
    assert probe.value is True
    on_change.assert_called_once_with(widget)


async def test_handler_replaced(widget, probe, on_change):
    "Replacing the handler calls only the new one"
    second = Mock()
    widget.on_change = second

    probe.press()
    await probe.redraw("Checkbox pressed")
    on_change.assert_not_called()
    second.assert_called_once_with(widget)


async def test_no_handler(widget, probe):
    "Without a handler the checkbox still toggles"
    widget.on_change = None
    probe.press()
    await probe.redraw("Checkbox pressed without handler")
    assert widget.value is True
