from cashd.app import start_cashd


def window():
    start_cashd(with_webview=True)


""" import runpy


def window():
    runpy._run_module_as_main("cashd") """
