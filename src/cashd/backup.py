from cashd.db import DB_ENGINE

import sqlite3
from os import path, makedirs, rename
from datetime import datetime
import shutil
import configparser
import logging


####################
# GLOBAL VARS
####################

SCRIPT_PATH = path.split(path.realpath(__file__))[0]
BACKUP_PATH = path.join(SCRIPT_PATH, "backup")
CONFIG_FILE = path.join(SCRIPT_PATH, "configs", "backup.ini")
LOG_FILE = path.join(SCRIPT_PATH, "logs", "backup.log")
DB_FILE = path.join(SCRIPT_PATH, "data", "database.db")

conf = configparser.ConfigParser()
conf.read(CONFIG_FILE, "utf-8")

makedirs(BACKUP_PATH, exist_ok=True)
for file in [CONFIG_FILE, LOG_FILE]:
    makedirs(path.split(file)[0], exist_ok=True)
    if not path.isfile(file):
        with open(file=file, mode="a"):
            pass

if not conf.has_section("default"):
    conf.add_section("default")
if not conf.has_option("default", "backup_places"):
    conf.set("default", "backup_places", "[]")

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


def parse_list_from_config(string: str) -> list[str]:
    """
    Transforma uma config com multiplos itens uma uma lista de strings
    do python.
    """
    logger.debug("function call: parse_list_from_config")
    string = string.replace("[", "").replace("]", "")
    list_of_items = string.split(",")
    return [i.strip() for i in list_of_items if i.strip() != ""]


def parse_list_to_config(list_: list) -> str:
    """
    Transforma uma lista de strings do python em uma config (str) com mais
    de um item.
    """
    string_list = (
        str(list_).replace("[", "[\n\t").replace(", ", ",\n\t").replace("'", "")
    )
    return string_list.replace("\\\\", "\\")


def copy_file(source_path, target_dir, _raise: bool = False):
    logger.debug("function call: copy_file")
    now = datetime.now()
    try:
        filename = f"backup_{now}.db".replace(":", "-")
        shutil.copyfile(source_path, path.join(target_dir, filename))
        logger.info(f"Copia de '{source_path}' criada em '{target_dir}'")
    except FileNotFoundError as xpt:
        logger.error(f"Erro realizando copia: {xpt}.", exc_info=1)
        if _raise:
            raise xpt


def rename_on_db_folder(current: str, new: str, _raise: bool = False):
    """
    Renomeia um arquivo na mesma pasta em que `DB_FILE` se encontra, se a
    operacao falhar porque o arquivo esta em uso, faz uma copia com o novo
    nome em vez de renomear.

    Levanta o erro que recebeu se ambas as operacoes falharem.
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
        logger.error(f"Erro renomeando {path_to_current}: {xpt}", exc_info=1)
        if _raise:
            raise xpt


def check_sqlite(file: str, _raise: bool = False):
    """Checa se o full path para o arquivo `file` representa um banco de dados."""
    logger.debug("function call: check_sqlite")

    if not path.isfile(file):
        xpt = FileExistsError(f"Arquivo {file} invalido.")
        logger.error(str(xpt))
        if _raise:
            raise xpt

    con = sqlite3.connect(file)
    cursor = con.cursor()
    stmt = f"PRAGMA schema_version;"
    try:
        _ = cursor.execute(stmt).fetchone()
        if _ == (0,):
            raise sqlite3.DatabaseError()
        return True
    except sqlite3.DatabaseError:
        return False
    except Exception as xpt:
        logger.critical(f"Erro inesperado validando {file}", exc_info=1)
        if _raise:
            raise xpt
    finally:
        con.close()


####################
# LEITURAS
####################


def read_db_size(file_path: str = DB_FILE) -> int:
    logger.debug("function call: read_db_size")
    try:
        size = path.getsize(file_path)
        return size
    except FileNotFoundError:
        logger.error(f"Arquivo '{file_path}' não encontrado.")
        return None


def read_last_recorded_size(config_file: str = CONFIG_FILE):
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
    config_file: str = CONFIG_FILE, current_size: int = read_db_size()
) -> None:
    """Writes current database size to `backup.ini`"""
    logger.debug("function call: write_current_size")
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


def write_add_backup_place(path: str):
    """Inclui o input `path` na opcao 'backup_places' em `backup.ini`"""
    logger.debug("function call: write_add_backup_place")
    conf.read(CONFIG_FILE, "utf-8")

    current_list_of_paths = parse_list_from_config(conf["default"]["backup_places"])

    if path in current_list_of_paths:
        logger.warning(f"'{path}' nao adicionado em 'backup_places', ja esta na lista")
        return

    new_list_of_paths = current_list_of_paths + [path]

    conf.set("default", "backup_places", parse_list_to_config(new_list_of_paths))
    with open(CONFIG_FILE, "w") as newconfig:
        conf.write(newconfig)


def write_rm_backup_place(idx: int):
    """Retira o `idx`-esimo item da lista 'backup_places' em `backup.ini`"""
    logger.debug("function call: write_rm_backup_place")
    try:
        idx = int(idx)
        if idx < 0:
            idx = idx * -1
    except:
        logger.error("Input invalido para 'write_rm_backup_place'")
        return
    conf.read(CONFIG_FILE, "utf-8")

    current_list_of_paths = parse_list_from_config(conf["default"]["backup_places"])
    _n_paths = len(current_list_of_paths)

    if (idx + 1) > _n_paths:
        logger.error(f"{idx} fora dos limites, deve ser menor que {_n_paths}")

    _ = current_list_of_paths.pop(idx)
    conf.set("default", "backup_places", parse_list_to_config(current_list_of_paths))
    with open(CONFIG_FILE, "w") as newconfig:
        conf.write(newconfig)


def load(file: str, _raise: bool = False) -> None:
    """
    Checa se `file` se trata de um banco de dados SQLite valido, e entao o
    carrega como o banco de dados atual no Cashd.

    Se um banco de dados ja estiver presente, vai renomea-lo para um nome
    nao usado pelo Cashd nem por outros arquivos na pasta e o mantera no
    diretorio.
    """
    logger.debug("function call: load")
    db_is_present = path.isfile(DB_FILE)
    file_is_valid = check_sqlite(file)

    if not file_is_valid:
        msg = f"Impossivel carregar arquivo nao SQLite {file}"
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


def run(force: bool = False, _raise: bool = False) -> None:
    """
    Vai fazer a copia do arquivo de banco de dados para a pasta local de backup
    e para as pastas listadas na opcao 'backup_places' em `backup.ini`.

    Usar `force = False` so vai fazer uma copia se o arquivo aumentou de
    tamanho, comparado com o registrado em 'file_sizes'.
    """
    conf.read(CONFIG_FILE, "utf-8")
    backup_places = parse_list_from_config(conf["default"]["backup_places"])
    error_was_raised = False

    if not force:
        current_size = read_db_size()
        previous_size = read_last_recorded_size()
        if current_size <= previous_size:
            return
        else:
            write_current_size(current_size=current_size)

    try:
        backup_places = [i for i in [BACKUP_PATH] + backup_places if i != ""]
        for place in backup_places:
            try:
                if path.exists(place):
                    copy_file(DB_FILE, place, _raise=_raise)
                else:
                    raise NotADirectoryError(f"{place} nao existe")
            except Exception as xpt:
                logger.error(f"Nao foi possivel salvar em '{place}': {xpt}", exc_info=1)
                if _raise:
                    error_was_raised = True
    except Exception as xpt:
        logger.error(f"Erro inesperado durante o backup: {xpt}", exc_info=1)
    finally:
        if error_was_raised:
            raise NotADirectoryError(
                f"Erro em alguma etapa do backup, verifique o log: {LOG_FILE}"
            )
