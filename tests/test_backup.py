from configparser import ConfigParser
from tempfile import TemporaryFile, TemporaryDirectory
import pytest
import sqlite3
import os

from cashd.backup import (
    conf,
    DB_FILE,
    CONFIG_FILE,
    BACKUP_PATH,
    read_db_size,
    write_current_size,
    parse_list_from_config,
    parse_list_to_config,
    copy_file,
    rename_on_db_folder,
    check_sqlite,
    read_last_recorded_size,
    write_add_backup_place,
    write_rm_backup_place,
    load,
    run,

)


SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]


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
    tempfile = TemporaryFile(delete=False)
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
    file = TemporaryFile(delete=False, dir=db_folder)
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
    
    # test invalid file
    try:
        rename_on_db_folder("not a file", "go brrrrr", _raise=True)
    except Exception:
        assert True == True
    else:
        raise AssertionError("Should raise an error with an invalid file")



def test_check_sqlite():
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

        # Test invalid database
        invalid_db_file = os.path.join(tempdir, "invalid_database.txt")
        with open(invalid_db_file, "wt"):
            assert check_sqlite(invalid_db_file) is False

        # Test exception when _raise=True
        try: 
            check_sqlite("oi", _raise=True)
        except Exception: pass
        else: raise AssertionError("Expected FileExistsError, but no exception was raised")

def test_read_db_size():
    # Create a temporary file
    with TemporaryFile(delete=False) as temp_file:
        temp_file.write(b"something")
        temp_file_path = temp_file.name

    # Test the function with an existing file
    size_existing = read_db_size(file_path=temp_file_path)
    assert size_existing == os.path.getsize(temp_file_path)

    # Test the function with a nonexistent file
    size_nonexistent = read_db_size(file_path="nonexistent_file.txt")
    assert size_nonexistent is None

    # Clean up the temporary file
    os.remove(temp_file_path)


def test_read_last_recorded_size_existing_section():
    # test existing section
    with TemporaryFile(delete=False) as temp_config_file:
        temp_config_file.write(b"[file_sizes]\ndbsize = 100\n")
        temp_config_file_path = temp_config_file.name

    size_existing = read_last_recorded_size(config_file=temp_config_file_path)
    assert size_existing == 100
    os.remove(temp_config_file_path)

    # test missing section
    with TemporaryFile(delete=False) as temp_config_file:
        temp_config_file.write(b"[other_section]\nkey = value\n")
        temp_config_file_path = temp_config_file.name

    size_nonexistent = read_last_recorded_size(config_file=temp_config_file_path)
    assert size_nonexistent == 0
    os.remove(temp_config_file_path)


def test_add_rm_backup_place():
    conf.read(CONFIG_FILE, "utf-8")
    current = parse_list_from_config(conf["default"]["backup_places"])
    path_to_add = r"C:\some\path\for\testing"

    # test add path to config
    write_add_backup_place(path_to_add)
    expected_add = current + [path_to_add]
    current_add = parse_list_from_config(conf["default"]["backup_places"])
    assert current_add == expected_add

    write_add_backup_place(path_to_add)
    current_add_repeated = parse_list_from_config(conf["default"]["backup_places"])
    # shall not add a path that already exists
    assert current_add_repeated == expected_add

    # test remove path from config
    added_idx = current_add.index(path_to_add)
    write_rm_backup_place(added_idx)
    current_rm = parse_list_from_config(conf["default"]["backup_places"])
    assert current_rm == current

    write_rm_backup_place("not even an index")
    # shall only perform action with valid indexes
    current_rm_invalid = parse_list_from_config(conf["default"]["backup_places"])
    assert current_rm_invalid == current_rm


def test_load():
    # test invalid file
    try:
        load(file="notfile", _raise=True)
    except OSError:
        assert True == True
    else:
        raise AssertionError("Should raise OSError")
    
    # test valid file
    dbdir = os.path.split(DB_FILE)[0]
    prev_stash = [f for f in os.listdir(dbdir) if "stash" in f]
    load(DB_FILE, _raise=True)
    new_stash = [f for f in os.listdir(dbdir) if "stash" in f]
    assert len(prev_stash) == len(new_stash) - 1

    # cleanup
    stashed = [f for f in new_stash if f not in prev_stash][0]
    os.remove(os.path.join(dbdir, stashed))
        
def test_run():
    # save current `backup_places`
    conf.read(CONFIG_FILE, "utf-8")
    prev_backup_places = parse_list_from_config(conf["default"]["backup_places"])

    # remove `backup_places` from config file
    curr_backup_places = parse_list_from_config(conf["default"]["backup_places"])
    while len(curr_backup_places) > 0:
        conf.read(CONFIG_FILE, "utf-8")
        write_rm_backup_place(0)
        curr_backup_places = parse_list_from_config(conf["default"]["backup_places"])
    
    # get current list of backups
    prev_saved_backups = os.listdir(BACKUP_PATH)

    # test invalid path
    write_add_backup_place("notpath")
    try:
        run(force=True, _raise=True)
    except NotADirectoryError:
        assert True == True
    else:
        raise AssertionError("Expected a NotADirectoryError")
    finally:
        write_rm_backup_place(0)

    # test valid path
    write_add_backup_place(SCRIPT_PATH)
    try:
        run(force=True, _raise=True)
    except Exception as err:
        raise AssertionError(f"Expected no exception, got {type(err)}: {str(err)}")
    finally:
        write_rm_backup_place(0)
    
    # restore `backup_places` and cleanup
    for path in prev_backup_places:
        write_add_backup_place(path)
    for file in [f for f in os.listdir(SCRIPT_PATH) if ".db" in f]:
        os.remove(os.path.join(SCRIPT_PATH, file))
    for file in [f for f in os.listdir(BACKUP_PATH) if f not in prev_saved_backups]:
        os.remove(os.path.join(BACKUP_PATH, file))
