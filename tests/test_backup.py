from configparser import ConfigParser
from tempfile import TemporaryFile, TemporaryDirectory
import pytest
import os

from cashd.backup import (
    read_db_size,
    write_current_size,
    parse_list_from_config,
    parse_list_to_config,
    copy_file
)


def test_dbsize_read():
    with TemporaryFile(delete=False) as data_file, TemporaryFile(delete=False) as config_file:
        data_file.write(b"testando um teste testoso...")
        write_current_size(
            config_file=config_file.name,
            current_size=read_db_size(file_path=data_file.name))
        config = ConfigParser()
        config.read(config_file.name)
        read_dbsize = int(config["file_sizes"]["dbsize"])
        assert  read_dbsize == read_db_size(file_path=data_file.name)


def test_list_parse():
    string = "[\n\tc:/some/path,\n\tc:\\some\\other\\path]"
    expected_list = [r"c:/some/path", r"c:\some\other\path"]

    parsed_from = parse_list_from_config(string)
    parset_to = parse_list_to_config(expected_list)
    assert parsed_from == expected_list
    assert parset_to == string


def test_copy_file():
    tempfile = TemporaryFile(delete_on_close=False)
    tempfile.close()
    with TemporaryDirectory() as tempdir:
        # test success
        copy_file(tempfile.name, tempdir)
        assert len(os.listdir(tempdir)) == 1
        # test fail
        try:
            copy_file("thisisnotevenapath", tempdir, True)
        except FileNotFoundError:
            assert 1 == 1
    os.unlink(tempfile.name)
