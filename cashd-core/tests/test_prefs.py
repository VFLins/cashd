import pytest
from os import path, unlink
from tempfile import TemporaryFile, TemporaryDirectory
from cashd_core.prefs import (
    PREFS_CONFIG_FILE,
    SettingsHandler,
    PreferencesHandler,
    BackupPrefsHandler,
    get_parser,
    _ConfigList,
    _ConfigInt,
    _ConfigBool,
)


CONFIGS_DIR = path.split(PREFS_CONFIG_FILE)[0]

SETTINGS_TEMPFILE = TemporaryFile(dir=CONFIGS_DIR)
PREFERENCES_TEMPFILE = TemporaryFile(dir=CONFIGS_DIR)
BACKUPPREFS_TEMPFILE = TemporaryFile(dir=CONFIGS_DIR)

settings_handler = SettingsHandler(path.split(SETTINGS_TEMPFILE.name)[1])
prefs_handler = PreferencesHandler(path.split(PREFERENCES_TEMPFILE.name)[1])
backup_prefs_handler = BackupPrefsHandler(path.split(BACKUPPREFS_TEMPFILE.name)[1])

handlers = [settings_handler, prefs_handler, backup_prefs_handler]


@pytest.mark.skip(reason="This is not a test function")
def test_parser():
    return get_parser(filename="test")


class TestConfigList(_ConfigList):
    __test__ = False

    def __init__(self):
        super().__init__(
            parser_factory=test_parser,
            section="list_test",
            key="words",
            default=["a", "beautiful", "list"],
        )


class TestConfigInt(_ConfigInt):
    __test__ = False

    def __init__(self):
        super().__init__(
            parser_factory=test_parser,
            section="int_test",
            key="level",
            default=8,
        )


class TestConfigBool(_ConfigBool):
    __test__ = False

    def __init__(self):
        super().__init__(
            parser_factory=test_parser,
            section="bool_test",
            key="important",
            default=False,
        )


def test_list_conf():
    try:
        # when calling `get` before any `set`, should retrieve the default value
        assert TestConfigList.get() == ["a", "beautiful", "list"]

        # section 'list_test' should exist after first use of TestConfigList
        conf_path, parser = test_parser()
        assert parser.has_section("list_test")

        # test if string was removed with `rm`
        TestConfigList.rm("a")
        assert TestConfigList.get() == ["beautiful", "list"]

        # test if string was added with `add`
        TestConfigList.add("config")
        assert TestConfigList.get() == ["beautiful", "list", "config"]

        # test if entrire list is replaced with `set`
        TestConfigList.set(["another", "completely", "different"])
        assert TestConfigList.get() == ["another", "completely", "different"]
    finally:
        # test cleanup
        if conf_path.is_file():
            conf_path.unlink()


def test_int_conf():
    try:
        # when calling `get` before any `set`, should retrieve the default value
        assert TestConfigInt.get() == 8

        # section 'int_test' should exist after first use of TestConfigInt
        conf_path, parser = test_parser()
        assert parser.has_section("int_test")

        # test if value is replaced with `set`
        TestConfigInt.set(12)
        assert TestConfigInt.get() == 12
    finally:
        # test cleanup
        if conf_path.is_file():
            conf_path.unlink()


def test_bool_conf():
    try:
        # when calling `get` before any `set`, should retrieve the default value
        assert TestConfigBool.get() == False

        # section 'bool_test' should exist after first use of TestConfigBool
        conf_path, parser = test_parser()
        assert parser.has_section("bool_test")

        # test if value is replaced with `set`
        TestConfigBool.set(True)
        assert TestConfigBool.get()
    finally:
        # test cleanup
        if conf_path.is_file():
            conf_path.unlink()


@pytest.mark.parametrize(
    "string,expected_list",
    [
        (
            "[\n\tc:/some/path,\n\tc:\\some\\other\\path]",
            [r"c:/some/path", r"c:\some\other\path"],
        ),
        ("[\n\t]", []),
        ("[\n\t]", []),
        ("[\n\tA:\\some\\path]", ["A:\\some\\path"]),
    ],
)
def test_list_parse(string: str, expected_list: list):
    parsed_from = settings_handler.parse_list_from_config(string)
    parsed_to = settings_handler.parse_list_to_config(expected_list)
    assert parsed_from == expected_list
    assert parsed_to == string


SETTINGS_TEMPFILE.close()
PREFERENCES_TEMPFILE.close()
BACKUPPREFS_TEMPFILE.close()

for handler in handlers:
    unlink(handler.config_file)
    unlink(handler.log_file)
