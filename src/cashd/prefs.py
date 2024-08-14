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


class PrefHandler:
    """
    Valores de configuração aceitos:
    [default]
    - limite_ultimas_transacs: `int`
    - uf_preferido: `str`
    - cidade_preferida: `str`
    """
    def __init__(self, config_file):
        self.conf = configparser.ConfigParser()
        self.conf.read(config_file, "utf-8")
        self.config_file = config_file
        try:
            self.conf.add_section("default")
        except configparser.DuplicateSectionError:
            pass

        self.logger = logging.getLogger(f"cashd.{__name__}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        log_fmt = logging.Formatter("%(asctime)s :: %(levelname)s %(message)s")
        log_handler = logging.FileHandler(LOG_FILE)
        log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(log_fmt)
        self.logger.addHandler(log_handler)


    def write_default(self, key: str, val: str):
        """Escreve a combinacao de `key` e `val` na categoria 'default'"""
        try:
            self.conf.set("default", key, val)
            with open(CONFIG_FILE, "a") as newconfig:
                self.conf.write(newconfig)
                self.conf.read(self.config_file, "utf-8")

        except Exception as xpt:
            self.logger.error(f"Erro inesperado: {str(xpt)}")
            raise xpt


    def read_default(self, key: str):
        try:
            return self.conf.get("default", key)
        except configparser.NoSectionError:
            return None
        except configparser.NoOptionError:
            return None


######################
### write defaults ###
######################

if not read_uf_preferido():
    write_uf_preferido("AC")

if not read_limite_ultimas_transacs():
    write_limite_ultimas_transacs(1000)