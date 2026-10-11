import os
import sys
import traceback
from pathlib import Path
from threading import Thread

import pytest
import toga

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TESTS_DIR = PROJECT_ROOT / "tests"


class TestApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = toga.Box()
        self.main_window.show()


def run_tests(app, args):
    os.chdir(PROJECT_ROOT)
    try:
        app.returncode = int(pytest.main([str(TESTS_DIR), *args]))
    except BaseException:
        traceback.print_exc()
        app.returncode = 1
    finally:
        # encerrar o app precisa acontecer na thread da interface
        app.loop.call_soon_threadsafe(app.exit)


def main():
    app = TestApp("Cashd Tests", "br.com.vitorlins.cashd.tests")
    app.returncode = 1
    thread = Thread(target=run_tests, args=(app, sys.argv[1:]))
    # Start pytest loop in the toga app's event loop
    app.add_background_task(lambda app, **kwargs: thread.start())
    app.main_loop()
    return app.returncode


if __name__ == "__main__":
    returncode = main()
    print(
        f">>>>>>>>>> EXIT {returncode} <<<<<<<<<<"
    )  # expected by briefcase dev --test
    sys.exit(returncode)
