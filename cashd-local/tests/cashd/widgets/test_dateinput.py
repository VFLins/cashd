from datetime import date
from unittest.mock import Mock

import pytest
import pytest_asyncio
import toga

from cashd.widget import DateInput

from ..probes import get_probe

INITIAL = date(2024, 5, 17)
MIN = date(2024, 1, 10)
MAX = date(2024, 12, 20)


def make_probe(widget):
    probe_class = get_probe("widget", "DateInput")
    return probe_class(widget)


@pytest.fixture
def on_change():
    return Mock()


@pytest_asyncio.fixture
async def widget(mainwindow, on_change):
    old_content = mainwindow.content
    widget = DateInput(value=INITIAL, min=MIN, max=MAX, on_change=on_change)
    mainwindow.content = toga.Box(children=[widget])
    yield widget
    mainwindow.content = old_content


@pytest.fixture
async def probe(widget):
    return make_probe(widget)


async def test_initial_state(widget, probe):
    "The widget shows the initial date, and the calendar starts on its month"
    await probe.redraw("DateInput should show the initial date")
    assert widget.value == INITIAL
    assert probe.text == probe.expected_text(INITIAL)
    assert probe.shown_month == (2024, 5)


async def test_default_value_is_today(mainwindow):
    "Without a value, the widget starts on today's date"
    old_content = mainwindow.content
    widget = DateInput()
    mainwindow.content = toga.Box(children=[widget])
    probe = make_probe(widget)
    await probe.redraw("DateInput with default value")

    assert widget.value == date.today()
    assert probe.text == probe.expected_text(date.today())

    mainwindow.content = old_content


async def test_value_by_code(widget, probe, on_change):
    "Changing the value in code updates the text and fires on_change once"
    new = date(2024, 8, 3)
    widget.value = new
    await probe.redraw("DateInput should show the new date")
    assert widget.value == new
    assert probe.text == probe.expected_text(new)
    assert probe.shown_month == (2024, 8)
    on_change.assert_called_once_with(widget)


async def test_same_value_no_event(widget, probe, on_change):
    "Setting the value it already has doesn't fire on_change"
    widget.value = INITIAL
    await probe.redraw("Value unchanged")
    on_change.assert_not_called()


async def test_typed_valid_date(widget, probe, on_change):
    "Typing a valid date and confirming commits it"
    new = date(2024, 7, 4)
    probe.type_text(probe.expected_text(new))
    await probe.redraw("Typed date should be committed")
    assert widget.value == new
    assert probe.text == probe.expected_text(new)
    on_change.assert_called_once_with(widget)


async def test_typed_invalid_text_restored(widget, probe, on_change):
    "Invalid text is discarded and the previous date is restored"
    probe.type_text("not a date")
    await probe.redraw("Invalid text should be restored")
    assert widget.value == INITIAL
    assert probe.text == probe.expected_text(INITIAL)
    on_change.assert_not_called()


async def test_typed_date_above_max_is_clamped(widget, probe, on_change):
    "A typed date after max is replaced by max"
    probe.type_text(probe.expected_text(date(2030, 1, 1)))
    await probe.redraw("Date should be clamped to max")
    assert widget.value == MAX
    assert probe.text == probe.expected_text(MAX)
    on_change.assert_called_once_with(widget)


async def test_typed_date_below_min_is_clamped(widget, probe):
    "A typed date before min is replaced by min"
    probe.type_text(probe.expected_text(date(2000, 1, 1)))
    await probe.redraw("Date should be clamped to min")
    assert widget.value == MIN


async def test_arrow_keys(widget, probe, on_change):
    "Up and Down arrows move the date by one day"
    assert probe.press_up() is True
    await probe.redraw("One day after")
    assert widget.value == date(2024, 5, 18)
    on_change.assert_called_once_with(widget)

    on_change.reset_mock()
    probe.press_down()
    probe.press_down()
    await probe.redraw("Two days before")
    assert widget.value == date(2024, 5, 16)
    assert on_change.call_count == 2


async def test_other_keys_ignored(widget, probe, on_change):
    "Keys other than Up/Down are left to the entry"
    from toga_gtk.libs import Gdk

    assert probe.press_key(Gdk.KEY_a) is False
    assert widget.value == INITIAL
    on_change.assert_not_called()


async def test_arrow_key_at_limit(widget, probe, on_change):
    "At max, the Up arrow doesn't move the date or fire on_change"
    widget.value = MAX
    on_change.reset_mock()

    probe.press_up()
    await probe.redraw("Date should stay at max")
    assert widget.value == MAX
    on_change.assert_not_called()


async def test_max_setter_clamps_value(widget, probe):
    "Lowering max below the value moves the value to max"
    widget.max = date(2024, 3, 1)
    await probe.redraw("Value should be clamped to the new max")
    assert widget.value == date(2024, 3, 1)
    assert probe.text == probe.expected_text(date(2024, 3, 1))


async def test_min_setter_clamps_value(widget, probe):
    "Raising min above the value moves the value to min"
    widget.min = date(2024, 6, 1)
    await probe.redraw("Value should be clamped to the new min")
    assert widget.value == date(2024, 6, 1)


async def test_calendar_navigation_keeps_value(widget, probe, on_change):
    "Navigating months changes the calendar page, not the value"
    probe.next_month()
    await probe.redraw("Calendar should show June")
    assert probe.shown_month == (2024, 6)
    assert widget.value == INITIAL
    assert probe.text == probe.expected_text(INITIAL)
    on_change.assert_not_called()

    probe.prev_month()
    probe.prev_month()
    await probe.redraw("Calendar should show April")
    assert probe.shown_month == (2024, 4)
    assert widget.value == INITIAL


async def test_navigation_buttons_respect_limits(widget, probe):
    "The month buttons are disabled in the min and max months"
    widget.value = date(2024, 1, 15) # MIN
    await probe.redraw("Calendar on the first allowed month")
    assert not probe.prev_enabled
    assert probe.next_enabled

    widget.value = date(2024, 12, 15) # MAX
    await probe.redraw("Calendar on the last allowed month")
    assert probe.prev_enabled
    assert not probe.next_enabled


async def test_calendar_click_selects_and_closes(widget, probe, on_change):
    "Clicking a day commits it and closes the popover"
    probe.open_popover()
    await probe.redraw("Popover should be open")

    probe.click_day(20)
    await probe.redraw("Day should be selected and popover closed")
    assert widget.value == date(2024, 5, 20)
    assert probe.text == probe.expected_text(date(2024, 5, 20))
    on_change.assert_called_once_with(widget)
    assert not probe.popover_visible


async def test_calendar_select_without_click_keeps_popover(widget, probe):
    "Selecting a day by code (no click) commits it without closing the popover"
    probe.open_popover()
    await probe.redraw("Popover should be open")

    probe.impl.calendar.select_day(22)
    await probe.redraw("Day committed, popover still open")
    assert widget.value == date(2024, 5, 22)
    assert probe.popover_visible


async def test_handler_replaced(widget, probe, on_change):
    "Replacing the handler calls only the new one"
    second = Mock()
    widget.on_change = second

    probe.press_up()
    await probe.redraw("Date changed")
    on_change.assert_not_called()
    second.assert_called_once_with(widget)
