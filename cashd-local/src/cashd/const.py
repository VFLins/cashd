from sys import platform
from toga.icons import Icon
from pathlib import Path
import subprocess


def sys_dark_mode() -> bool:
    """Detects if dark mode is currently enabled in the OS.

    :returns: `True` if dark mode is enabled, `False` otherwise.
    """
    match platform:
        case "linux":
            return _linux_dark_mode()
        case "win32":
            return False  # ignore while dark theme is not implemented for winforms
            # return _windows_dark_mode()
        case _:
            Warning(f"Not capable of detecting {platform=} dark mode.")
            return False


def _windows_dark_mode() -> bool:
    """Dectects if dark mode is enabled in a Windows system."""
    # stackoverflow.com/a/65349866
    # github.com/albertosottile/darkdetect/blob/master/darkdetect/_windows_detect.py
    try:
        import winreg
    except ImportError:
        return False
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        subkey = winreg.QueryValueEx(key=key, name="AppsUseLightTheme")[0]
        # subkey value is 1 when the system is using light mode
        return subkey == 0
    except FileNotFoundError:
        # assume light mode when key is not found
        return False


def _linux_dark_mode() -> bool:
    """Detects if dark mode is enabled in a GTK3/4 based GNU/Linux system.
    Will depend on `gsettings` being installed in the system to work properly.
    """
    result = subprocess.run(
        ["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"],
        capture_output=True,
        text=True,
    )
    return "dark" in result.stdout.lower()


RESOURCES_DIR = Path(Path(__file__).parent, "resources")

ICON_TRANSAC = Icon(path=Path(RESOURCES_DIR, "TransacaoBranco"), system=True)
ICON_CONTAS = Icon(path=Path(RESOURCES_DIR, "ContasBranco"), system=True)
ICON_STATS = Icon(path=Path(RESOURCES_DIR, "DadosBranco"), system=True)
ICON_CONFIG = Icon(path=Path(RESOURCES_DIR, "ConfiguracaoBranco"), system=True)
ICON_RETURN = Icon(
    path=Path(RESOURCES_DIR, "arrow-left-dark" if sys_dark_mode() else "arrow-left"),
    system=True,
)
ICON_USER_OPTS = Icon(
    path=Path(RESOURCES_DIR, "user-pen-dark" if sys_dark_mode() else "user-pen"),
    system=True,
)

FONT_SIZE = 10
MAIN_WINDOW_SIZE = (660, 560)

NA_VALUE = "N/D"
MAX_ALLOWED_VALUE = 99999999
SMALL_FONT_SIZE = abs(FONT_SIZE * 0.8)
BIG_FONT_SIZE = abs(FONT_SIZE * 1.15)
CONTENT_WIDTH = 560
FORM_WIDTH = 395

ESTADOS = [
    "AC",
    "AL",
    "AP",
    "AM",
    "BA",
    "CE",
    "DF",
    "ES",
    "GO",
    "MA",
    "MT",
    "MS",
    "MG",
    "PA",
    "PB",
    "PR",
    "PE",
    "PI",
    "RJ",
    "RN",
    "RS",
    "RO",
    "RR",
    "SC",
    "SP",
    "SE",
    "TO",
]
