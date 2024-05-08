from os import path, makedirs, remove
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
conf.read(CONFIG_FILE, "utf-8")

makedirs(BACKUP_PATH, exist_ok = True)
for file in [CONFIG_FILE, LOG_FILE]:
    makedirs(path.split(file)[0], exist_ok=True)
    if not path.isfile(file):
        with open(file=file, mode="a"):
            pass

logger = logging.getLogger("cashd.backup")
logger.setLevel(logging.DEBUG)
logger.propagate = False

log_fmt = logging.Formatter("%(asctime)s :: %(levelname)s %(message)s")
log_handler = logging.FileHandler(LOG_FILE)
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(log_fmt)

logger.addHandler(log_handler)


def parse_list_from_config(string: str) -> list[str]:
    """Transforms a config with multiple items in a python list of strings."""
    string = string\
        .replace("[", "")\
        .replace("]", "")
    list_of_items = string.split(",")
    return [i.strip() for i in list_of_items]


def parse_list_to_config(list_: list) -> str:
    string_list = str(list_)\
        .replace("[", "[\n\t")\
        .replace(", ", ",\n\t")\
        .replace("'", "")
    return string_list.replace("\\\\", "\\")


def copy_file(source_path, target_dir):
    try:
        shutil.copyfile(source_path, path.join(target_dir, "database.db"))
        logger.info(f"Copia de '{source_path}' criada em '{target_dir}'")

    except FileNotFoundError as err:
        logger.error(f"Erro realizando copia: {err}.")


####################
# LEITURAS
####################

def read_db_size(file_path: str = DB_FILE) -> int:
    try:
        size = path.getsize(file_path)
        return size

    except FileNotFoundError:
        logger.error(f"Arquivo '{file_path}' não encontrado.")
        return None


def read_last_recorded_size(config_file: str = CONFIG_FILE):
    config = configparser.ConfigParser()
    config.read(config_file)

    if "file_sizes" in config:
        return config["file_sizes"].getint("dbsize", fallback=None)

    return 0


####################
# ESCRITAS
####################

def write_current_size(
        config_file: str = CONFIG_FILE,
        current_size: int = read_db_size()
    ) -> None:
    """Writes current database size to `backup.ini`"""
    conf.read(config_file)

    try:
        conf.add_section("file_sizes")
    except configparser.DuplicateSectionError:
        pass
    except Exception as xpt:
        logger.error(f"Erro inesperado criando a seção `file_sizes`: {xpt}")

    conf["file_sizes"]["dbsize"] = str(current_size)
    with open(config_file, "w") as config_writer:
        conf.write(config_writer)


def write_backup_place(path: str):
    conf.read(CONFIG_FILE, "utf-8")

    current_list_of_paths = parse_list_from_config(
        conf["default"]["backup_places"])

    if path in current_list_of_paths:
        logger.warn(
            f"'{path}' nao adicionado em 'backup_places', ja esta na lista")
        return
    
    new_list_of_paths = current_list_of_paths + [path]

    conf.set(
        "default",
        "backup_places",
        parse_list_to_config(new_list_of_paths))
    with open(CONFIG_FILE, "w") as newconfig:
        conf.write(newconfig)


def run(
        backup_places: list[str] = parse_list_from_config(conf['default']['backup_places']),
        db_path: str = DB_FILE
    ) -> None:
    conf.read(CONFIG_FILE, "utf-8")

    check_size = conf["default"].getboolean("check_file_size", fallback=None)
    #if check_size:
    #    current_size = read_db_size()
    #    previous_size = read_last_recorded_size()
    #else:
    current_size, previous_size = 1, 0
    
    if current_size > previous_size:
        try:
            backup_places = [BACKUP_PATH] + backup_places
            print(backup_places)
            for place in backup_places:
                try:
                    copy_file(db_path, place)
                except Exception as xpt:
                    logger.error(f"Nao foi possivel salvar copia em {place}")


            # Atualize o tamanho anterior e salve no arquivo de configuração
            write_current_size(current_size=current_size)
            print("Backups criados com sucesso!")

        except Exception:
            logger.error("Nao foi possível obter o tamanho do arquivo.")
    