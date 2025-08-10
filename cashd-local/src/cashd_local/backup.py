from cashd.prefs import BackupPrefsHandler

from os import path, rename, makedirs
from datetime import datetime
import configparser
import sqlite3
import logging
import shutil


####################
# GLOBAL VARS
####################

SCRIPT_PATH = path.split(path.realpath(__file__))[0]
BACKUP_PATH = path.join(SCRIPT_PATH, "data", "backup")
CONFIG_FILE = path.join(SCRIPT_PATH, "configs", "backup.ini")
LOG_FILE = path.join(SCRIPT_PATH, "logs", "backup.log")
DB_FILE = path.join(SCRIPT_PATH, "data", "database.db")

makedirs(BACKUP_PATH, exist_ok=True)

settings = BackupPrefsHandler()

logger = logging.getLogger("cashd.backup")
logger.setLevel(logging.DEBUG)
logger.propagate = False

log_fmt = logging.Formatter("%(asctime)s :: %(levelname)s %(message)s")
log_handler = logging.FileHandler(LOG_FILE)
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(log_fmt)

logger.addHandler(log_handler)


####################
# UTILS
####################


class BackupPlacesSource:
    def __init__(self):
        """Mimics `cashd.db._DataSource` behavior providing interaction to the
        list of backup places.
        """

    @property
    def current_data(self) -> list[str]:
        return settings.read_backup_places()


def copy_file(source_path: str, target_dir: str, _raise: bool = False):
    """Copies a file to `target_dir`.

    :param source_path: Full path to the file to be copied.
    :param target_dir: Directory where the file will be copied into.
    :param _raise: Boolean indicating if errors should also be raised, if false, errors
      will only be silently logged to a log file.

    :raises NotADirectoryError: If `target_dir` is not a valid directory and `_raise=True`.
    :raises FileNotFoundError: If `source_path` is not a valid file and `_raise=True`.
    """
    logger.debug("function call: copy_file")
    if not path.exists(target_dir):
        err_msg = f"'{target_dir}' does not exist."
        logger.error(err_msg)
        if _raise:
            raise NotADirectoryError(err_msg)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
    try:
        filename = f"backup_{now}.db"
        shutil.copyfile(source_path, path.join(target_dir, filename))
        logger.info(f"Copia de '{source_path}' criada em '{target_dir}'")
    except FileNotFoundError as xpt:
        logger.error(f"Erro realizando copia: {xpt}.", exc_info=True)
        if _raise:
            raise xpt


def rename_on_db_folder(current: str, new: str, _raise: bool = False):
    """Renames a file in the same folder where `DB_FILE` is located. If the renaming
    operation fails because the file is in use, it makes a copy with the new name instead
    of renaming.

    :param current: Current name of the file.
    :param new: Name that the file will be renamed into.
    :param _raise: Boolean indicating if errors should also be raised, if false, errors
      will only be silently logged to a log file.

    :raises: The last error received if both operations fail and `_raise=True`.
    """
    logger.debug("function call: rename_on_db_folder")
    current, new = str(current), str(new)

    db_folder = path.split(DB_FILE)[0]
    path_to_current = path.join(db_folder, current)
    path_to_new = path.join(db_folder, new)

    try:
        rename(path_to_current, path_to_new)
        logger.info(f"{path_to_current} renomeado como {path_to_new}")
    except WindowsError:
        shutil.copy(path_to_current, path_to_new)
    except Exception as xpt:
        logger.error(f"Erro renomeando {path_to_current}: {xpt}", exc_info=True)
        if _raise:
            raise xpt


def check_sqlite(file: str, _raise: bool = False) -> bool | None:
    """Checks if `file` represents a sqlite database. All unexpected errors are only
    logged to `backup.log`, but can also be raised if  `_raise=True`.

    :param file: Path to the file to be checked.
    :param _raise: Boolean indicating if errors should also be raised, if false, errors
      will only be silently logged to a log file.

    :returns: A boolean value indicating if `file` is a SQLite database, or None if an
      unexpected error is catched.
    """
    logger.debug("function call: check_sqlite")
    if not path.exists(file):
        msg = f"{file=} does not exist."
        logger.error(msg)
        if _raise:
            raise FileExistsError(msg)
    try:
        con = sqlite3.connect(file)
    except sqlite3.OperationalError as err:
        return False
    cursor = con.cursor()
    try:
        res = cursor.execute(f"PRAGMA schema_version;").fetchone()[0]
        return type(res) is int
    except sqlite3.DatabaseError as err:
        return False
    except Exception as err:
        logger.critical(
            f"Unexpected error validating {file}: {str(err)}", exc_info=True
        )
        if _raise:
            raise err
        return None
    finally:
        con.close()


def read_db_size(file_path: str = DB_FILE) -> int:
    """Gives the size (kilobytes) of the provided file, 0 (zero) if it doesn't exist."""
    logger.debug("function call: read_db_size")
    try:
        return path.getsize(file_path)
    except Exception as xpt:
        logger.error(f"Erro lendo tamanho do arquivo: {str(xpt)}")
        return 0


####################
# LEITURAS
####################


def read_last_recorded_size(config_file: str = CONFIG_FILE):
    """Reads last recorded DB file size from config file."""
    logger.debug("function call: read_last_recorded_size")
    config = configparser.ConfigParser()
    config.read(config_file)
    if "file_sizes" in config:
        return config["file_sizes"].getint("dbsize", fallback=None)
    return 0


####################
# ESCRITAS
####################


def write_current_size(
    current_size: int | None = read_db_size(), settings: BackupPrefsHandler = settings
) -> None:
    """Writes current database size to `backup.ini`."""
    logger.debug("function call: write_current_size")
    settings.write_dbsize(current_size)


def write_add_backup_place(path: str, settings: BackupPrefsHandler = settings) -> None:
    """Includes the input `path` in the 'backup_places' option in `backup.ini`."""
    logger.debug("function call: write_add_backup_place")
    settings.add_backup_place(path)


def write_rm_backup_place(idx: int, settings: BackupPrefsHandler = settings) -> None:
    """Removes the `idx`-th item from the 'backup_places' list in `backup.ini`."""
    logger.debug("function call: write_rm_backup_place")
    settings.rm_backup_place(idx)


def load(file: str, _raise: bool = False) -> None:
    """If `file` is a valid SQLite database, loads it as the current database in Cashd.
    If a database is already present, it will be renamed to a unique name and will be
    kept in the directory.

    :param file: Full path to the file that be loaded as the new database.
    :param _raise: All unexpected errors are only logged to `backup.log`, but can also
      be raised if `_raise=True`.
    """
    logger.debug("function call: load")
    db_is_present = path.isfile(DB_FILE)

    if not check_sqlite(file):
        msg = f"Cannot load non-SQLite file: '{file}'."
        logger.error(msg)
        if _raise:
            raise OSError(msg)

    if db_is_present:
        now = datetime.now()
        dbfilename = path.split(DB_FILE)[1]
        stashfilename = f"stashed{now}.db".replace(":", "-")
        rename_on_db_folder(dbfilename, stashfilename)

    try:
        shutil.copyfile(file, DB_FILE)
    except shutil.SameFileError:
        pass


def run(
    force: bool = False, settings: BackupPrefsHandler = settings, _raise: bool = False
) -> None:
    """Copies the database file to the local backup folder and to the folders listed in
    the 'backup_places' option in `backup.ini`.

    :param force: Using `force=False` will only make a copy if the file has increased in
      size, compared to what's recorded in 'file_sizes'. Otherwise, will copy anyway.
    :param settings: Settings handler that will be used to read the database file's size.
    :param _raise: All unexpected errors are only logged to `backup.log`, but can also be
      raised if `_raise=True`.
    """
    backup_places: list = settings.read_backup_places()
    error_was_raised = False

    current_size = read_db_size()
    previous_size = settings.read_dbsize()

    if not force:
        if current_size <= previous_size:
            return
    settings.write_dbsize(current_size)

    try:
        backup_places = [i for i in [BACKUP_PATH] + backup_places if i != ""]
        for place in backup_places:
            try:
                copy_file(DB_FILE, place, _raise=_raise)
            except Exception as err:
                logger.error(
                    f"Nao foi possivel salvar em '{place}': {err}", exc_info=True
                )
                if _raise:
                    error_was_raised = True
    except Exception as err:
        logger.error(f"Erro inesperado durante o backup: {err}", exc_info=True)
    finally:
        if error_was_raised:
            raise NotADirectoryError(
                f"Erro em alguma etapa do backup, verifique o log: {LOG_FILE}"
            )
