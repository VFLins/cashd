from os import path, makedirs, rename
from datetime import datetime
import shutil
import configparser
import logging


####################
# GLOBAL VARS
####################

SCRIPT_PATH = path.split(path.realpath(__file__))[0]
CONFIG_FILE = path.join(SCRIPT_PATH, "configs", "prefs.ini")
LOG_FILE = path.join(SCRIPT_PATH, "logs", "prefs.log")
DB_FILE = path.join(SCRIPT_PATH, "data", "database.db")

for file in [CONFIG_FILE, LOG_FILE]:
    makedirs(path.split(file)[0], exist_ok=True)
    if not path.isfile(file):
        with open(file=file, mode="a"):
            pass

conf = configparser.ConfigParser()
conf.read(CONFIG_FILE, "utf-8")

logger = logging.getLogger("cashd.prefs")
logger.setLevel(logging.DEBUG)
logger.propagate = False

log_fmt = logging.Formatter("%(asctime)s :: %(levelname)s %(message)s")
log_handler = logging.FileHandler(LOG_FILE)
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(log_fmt)

logger.addHandler(log_handler)


def write_uf_preferido(val: str):
    """Define `val` como o valor no campo [Default] `uf_preferido`"""
    logger.debug("function call: write_uf_preferido")
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, "utf-8")
            
    config["default"] = {"uf_preferido": val}
    with open(CONFIG_FILE, "w") as newconfig:
        config.write(newconfig)


def read_uf_preferido() -> str:
    """Retorna o valor de `uf_preferido` em 'prefs.ini' como `str`"""
    logger.debug("function call: read_uf_preferido")
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, "utf-8")

    try:
        return config.get("default", "uf_preferido")
    except configparser.NoSectionError:
        return ""