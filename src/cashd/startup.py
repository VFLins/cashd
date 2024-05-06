from cashd.app import start_cashd
import sys


def window():
    if "window" in sys.argv:
        start_cashd(with_webview=True)
        return

    if "browser" in sys.argv:
        start_cashd(with_webview=False)
        return
