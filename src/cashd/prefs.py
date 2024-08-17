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


class SettingsHandler:
    """
    Valores de configuração usados:

    ### prefs.ini

    `[default]`
    - last_transacs_limit: `int`
    - main_state: `str`
    - main_city: `str`

    ### backup.ini

    `[default]`
    - run_after_closing: `bool`
    - check_file_size: `bool`
    - backup_places: `list`

    `[data]`
    - dbsize: `int`
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

    def parse_list_from_config(string: str) -> list[str]:
        """
        Transforma uma config com multiplos itens uma uma lista de strings
        do python.
        """
        string = string.replace("[", "").replace("]", "")
        list_of_items = string.split(",")
        return [i.strip() for i in list_of_items if i.strip() != ""]

    def parse_list_to_config(list_: list[str]) -> str:
        """
        Transforma uma lista de strings do python em uma config (str) com mais
        de um item.
        """
        string_list = (
            str(list_).replace("[", "[\n\t").replace(", ", ",\n\t").replace("'", "")
        )
        return string_list.replace("\\\\", "\\")

    def _write(self, sect: str, key: str, val: str):
        """Escreve a combinacao de `key` e `val` na seção `sect`"""
        try:
            self.conf.set(sect, key, val)
            with open(CONFIG_FILE, "a") as newconfig:
                self.conf.write(newconfig)
            self.conf.read(self.config_file, "utf-8")

        except Exception as xpt:
            self.logger.error(f"Erro escrevendo [{sect}] {key}={val}: {str(xpt)}")
            raise xpt

    def _read(self, sect: str, key: str, convert_to=None):
        try:
            if not convert_to:
                return self.conf.get(sect, key)
            elif convert_to == "bool":
                return self.conf.getboolean(sect, key)
            elif convert_to == "int":
                return self.conf.getint(sect, key)
            elif convert_to == "list":
                return self.parse_list_from_config(self.conf.get(sect, key))

        except configparser.NoSectionError:
            return None
        except configparser.NoOptionError:
            return None

    def _add_to_list(self, sect: str, key: str, val: str):
        current_list = self.parse_list_from_config(self.conf[sect][key])
        new_list = set(current_list + [val])

        self.conf.set(sect, key, self.parse_list_to_config(new_list))
        with open(CONFIG_FILE, "w") as newconfig:
            self.conf.write(newconfig)
        self.conf.read(self.config_file, "utf-8")

    def _rm_from_list(self, sect: str, key: str, idx: int):
        """Retira o `idx`-esimo item da lista"""
        current_list = self.parse_list_from_config(self.conf[sect][key])
        n = len(current_list)

        if (idx + 1) > n:
            self.logger.error(f"{idx} fora dos limites, deve ser menor que {n}")

        _ = current_list.pop(idx)
        self.conf.set(sect, key, self.parse_list_to_config(current_list))
        with open(CONFIG_FILE, "w") as newconfig:
            self.conf.write(newconfig)
        self.conf.read(self.config_file, "utf-8")

    def write_limite_ultimas_transacs(self, val: int):
        """
        Define um limite de transações a ser exibidas na tabela
        'Últimas transações'.
        """
        val = int(val)
        self._write("default", "limite_ultimas_transacs", str(val))

    def write_uf_preferido(self, val: str):
        """Define o UF padrão exibido no formulário 'Criar conta'"""
        self._write("default", "uf_preferido", val)

    def write_cidade_preferida(self, val: str):
        """Define a cidade padrão exibida no formulário 'Criar conta'"""
        self._write("default", "cidade_preferida", val)

    def read_limite_ultimas_transacs(self) -> int | None:
        self._read("default", "limite_ultimas_transacs", convert_to="int")

    def read_uf_preferido(self) -> str | None:
        self._read("default", "uf_preferido")

    def read_cidade_preferida(self) -> str | None:
        self._read("default", "cidade_preferida")


######################
### write defaults ###
######################

prefs_ = SettingsHandler(config_file=CONFIG_FILE)

if not prefs_.read_uf_preferido():
    prefs_.write_uf_preferido("AC")

if not prefs_.read_cidade_preferida():
    prefs_.write_cidade_preferida("")

if not prefs_.read_limite_ultimas_transacs():
    prefs_.write_limite_ultimas_transacs(1000)
