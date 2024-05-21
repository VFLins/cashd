from configparser import ConfigParser
from tempfile import TemporaryFile, TemporaryDirectory
import pytest
import sqlite3
import os

from cashd.backup import (
    read_db_size,
    write_current_size,
    parse_list_from_config,
    parse_list_to_config,
    copy_file,
    rename_on_db_folder,
    check_sqlite,
    DB_FILE
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
    parsed_to = parse_list_to_config(expected_list)
    assert parsed_from == expected_list
    assert parsed_to == string


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


def test_rename_on_db_folder():
    db_folder = os.path.split(DB_FILE)[0]
    
    # test closed file
    file = TemporaryFile(delete_on_close=False, dir=db_folder)
    file.close()
    old_filename = os.path.split(file.name)[1]
    new_filename = "renamed.file"
    rename_on_db_folder(old_filename, new_filename)
    new_filepath = os.path.join(db_folder, new_filename)
    assert os.path.isfile(new_filepath)
    os.unlink(new_filepath)

    # test open file
    with TemporaryFile(dir=db_folder) as file:
        old_filename = os.path.split(file.name)[1]
        new_filename = "renamed.file"
        rename_on_db_folder(old_filename, new_filename)
        new_filepath = os.path.join(db_folder, new_filename)
        assert os.path.isfile(new_filepath)


def test_check_sqlite():
    tempdir = TemporaryDirectory()
    with TemporaryDirectory() as tempdir:
        # Create a valid SQLite database file
        valid_db_file = os.path.join(tempdir, "valid_database.db")
        con = sqlite3.connect(valid_db_file)
        cursor = con.cursor()
        cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        con.commit()
        con.close()

        # Test valid database
        assert check_sqlite(valid_db_file) is True

        # Create an empty file (invalid database)
        invalid_db_file = os.path.join(tempdir, "invalid_database.txt")
        open(invalid_db_file, "wt").close()

        # Test invalid database
        assert check_sqlite(invalid_db_file) is False

        # Test exception when _raise=True
        with open(os.path.join(tempdir, "non_existent.db"), "w"):
            pass
        try:
            check_sqlite(invalid_db_file, _raise=True)
        except FileExistsError:
            pass
        else:
            raise AssertionError("Expected FileExistsError, but no exception was raised")
