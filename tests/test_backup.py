from configparser import ConfigParser
from tempfile import TemporaryFile
import pytest
from cashd.backup import (
    get_db_size,
    write_current_size,
    parse_list_config
)


def test_dbsize_read():
    with TemporaryFile(delete=False) as data_file, TemporaryFile(delete=False) as config_file:
        data_file.write(b"testando um teste testoso...")

        write_current_size(
            config_file=config_file.name,
            current_size=get_db_size(file_path=data_file.name))
        
        config = ConfigParser()
        config.read(config_file.name)
        read_dbsize = int(config["file_sizes"]["dbsize"])

        assert  read_dbsize == get_db_size(file_path=data_file.name)


@pytest.mark.parametrize("string, expected_list", [
    (
        r"[c:\user\path\to\folder, c:\path\to\file.ext]",
        ["c:\\user\\path\\to\\folder", "c:\\path\\to\\file.ext"]
    ),
    (
        "[\n\tc:/some/path,\n\tc:\\some\\other\\path]",
        [r"c:/some/path", r"c:\some\other\path"]
    )
])
def test_list_parse(string, expected_list):
    parsed_list = parse_list_config(string)
    assert parsed_list == expected_list


def test_write_list():
    pass