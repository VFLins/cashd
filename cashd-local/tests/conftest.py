import pytest
import toga
from tests.cashd.probes import get_probe


@pytest.fixture(scope="session")
def app():
    return toga.App.app


@pytest.fixture
def main_window(app):
    return app.main_window


@pytest.fixture(scope="session")
def probe():
    return get_probe("PlatformProbe")
