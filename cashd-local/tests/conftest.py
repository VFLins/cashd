import toga
import pytest
import asyncio
from dataclasses import dataclass
from tests.cashd.probes import get_probe

try:
    from gi.events import GLibEventLoopPolicy
except ImportError:  # outro backend (WinForms etc.)
    GLibEventLoopPolicy = None

if GLibEventLoopPolicy is not None:
    _original_set_event_loop = GLibEventLoopPolicy.set_event_loop

    def _set_event_loop(self, loop):
        # O proxy não executa nada nesta thread; não registra como loop da thread.
        if isinstance(loop, ProxyEventLoop):
            return
        return _original_set_event_loop(self, loop)

    GLibEventLoopPolicy.set_event_loop = _set_event_loop


@pytest.fixture(scope="session")
def app():
    return toga.App.app


@pytest.fixture
def mainwindow(app):
    return app.main_window

@dataclass
class ProxyTask:
    coro: object
    kwargs: dict
    _source_traceback = None  # exigido por asyncio.ensure_future

    def done(self):
        return False


@dataclass
class ProxyEventLoop(asyncio.AbstractEventLoop):
    """Entrega as corrotinas ao loop do app, que roda na thread da interface."""

    closed: bool = False

    def create_task(self, coro, **kwargs):
        return ProxyTask(coro, kwargs)

    def run_until_complete(self, future):
        if asyncio.iscoroutine(future):
            coro = future
        elif isinstance(future, ProxyTask):
            coro = future.coro
        else:
            raise TypeError(f"Cannot run {future!r} on the proxy loop")

        loop = toga.App.app._impl.loop
        return asyncio.run_coroutine_threadsafe(coro, loop).result()

    async def shutdown_asyncgens(self):
        pass

    async def shutdown_default_executor(self, timeout=None):
        pass

    def set_debug(self, enabled):
        pass

    def is_closed(self):
        return self.closed

    def close(self):
        self.closed = True


def pytest_asyncio_loop_factories(config, item):
    return {"proxy": ProxyEventLoop}
