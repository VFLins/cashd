import pytest
import toga
from tests.cashd.probes import get_probe


@pytest.fixture(scope="session")
def app():
    return toga.App.app


@pytest.fixture
def mainwindow(app):
    return app.main_window
