from os import path, makedirs
import shutil
import configparser
import logging


# global vars
SCRIPT_PATH = path.split(path.realpath(__file__))[0]
BACKUP_PATH = path.join(SCRIPT_PATH, "backup")
CONFIG_FILE = path.join(SCRIPT_PATH, "configs", "backup.ini")
LOG_FILE = path.join(SCRIPT_PATH, "logs", "backup.log")
DB_FILE = path.join(SCRIPT_PATH, "data", "database.db")

conf = configparser.ConfigParser()
conf.read(CONFIG_FILE)

makedirs(BACKUP_PATH, exist_ok = True)
for file in [CONFIG_FILE, LOG_FILE]:
    makedirs(path.split(file)[0], exist_ok=True)
    if not path.isfile(file):
        with open(file=file, mode="a"):
            pass

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s :: %(message)s")
logging.getLogger().propagate = False


def get_db_size(file_path: str = DB_FILE):
    try:
        size = path.getsize(file_path)
        return size

    except FileNotFoundError:
        logging.error(f"Arquivo '{file_path}' não encontrado.")
        return None


def parse_list_config(string: str) -> list[str]:
    """Transforms a config with multiple items in a python list"""
    string = string\
        .replace("[", "")\
        .replace("]", "")
    list_of_items = string.split(",")
    return [i.strip() for i in list_of_items]


def copy_file(source_path, target_dir):
    try:
        shutil.copy(source_path, target_dir)
        logging.info(f"Cópia de '{source_path}' criada em '{target_dir}'")

    except FileNotFoundError:
        logging.error(f"Arquivo '{source_path}' não encontrado.")

def read_last_recorded_size(config_file: str = CONFIG_FILE):
    config = configparser.ConfigParser()
    config.read(config_file)

    if "file_sizes" in config:
        return config["file_sizes"].getint("dbsize", fallback=None)

    return 0


def write_current_size(
        config_file: str = CONFIG_FILE,
        current_size: int = get_db_size()
    ) -> None:
    """Writes current database size to `backup.ini`"""
    config = configparser.ConfigParser()
    config.read(config_file)

    if "file_sizes" not in config:
        config["file_sizes"] = {}

    config["file_sizes"]["dbsize"] = str(current_size)
    with open(config_file, "w") as config_writer:
        config.write(config_writer)

def run(
        backup_places: list[str] = parse_list_config(conf['default']['backup_places']),
        config_file: str = CONFIG_FILE,
        db_path: str = DB_FILE
    ) -> None:
    config = configparser.ConfigParser()
    config.read(config_file)

    check_size = config["default"].getboolean("check_file_size", fallback=None)
    if check_size:
        current_size = get_db_size()
        previous_size = read_last_recorded_size()

    else:
        current_size = 1
        previous_size = 0
    
    if current_size > previous_size:
        try:
            backup_places = backup_places + [BACKUP_PATH]
            for place in backup_places:
                copy_file(db_path, place)

            # Atualize o tamanho anterior e salve no arquivo de configuração
            write_current_size(current_size=current_size)
            print("Backups criados com sucesso!")

        except Exception:
            logging.error("Não foi possível obter o tamanho do arquivo.")
    