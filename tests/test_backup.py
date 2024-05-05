import unittest
from configparser import ConfigParser
from tempfile import TemporaryFile
from cashd.backup import (
    get_db_size,
    write_current_size,
)


def test_dbsize_read():
    with TemporaryFile() as data_file, TemporaryFile() as config_file:
        data_file.write(b"testando um teste testoso...")

        write_current_size(
            config_file=config_file.name,
            current_size=get_db_size(file_path=data_file.name))
        
        parser = ConfigParser()
        parser.read(config_file.name)
        read_dbsize = int(parser["file_sizes"]["dbsize"])

        assert  read_dbsize == get_db_size(file_path=data_file.name)