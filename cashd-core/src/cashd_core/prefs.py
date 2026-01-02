from os import path, makedirs
from sys import platform
from pathlib import Path
from typing import Literal
import configparser
import logging


if platform == "win32":
    CASHD_FILES_PATH = Path.home().joinpath("AppData", "Local", "Cashd")
    CONFIG_PATH = Path(CASHD_FILES_PATH, "configs")
    LOG_PATH = Path(CASHD_FILES_PATH, "logs")
else:
    CASHD_FILES_PATH = Path.home().joinpath(".local", "share", "Cashd")
    CONFIG_PATH = Path.home().joinpath(".config", "Cashd")
    LOG_PATH = Path.home().joinpath(".local", "state", "Cashd", "logs")

PREFS_CONFIG_FILE = Path(CONFIG_PATH, "prefs.ini")
BACKUP_CONFIG_FILE = Path(CONFIG_PATH, "backup.ini")
LOG_FILE = path.join(LOG_PATH, "prefs.log")
DB_FILE = path.join(CASHD_FILES_PATH, "data", "database.db")

for dirpath in [CASHD_FILES_PATH, LOG_PATH, CONFIG_PATH]:
    makedirs(dirpath, exist_ok=True)


class SettingsHandler:
    """
    Valores de configuração usados:

    ### prefs.ini

    `[default]`
    - last_transacs_limit: `int`
    - highest_balaces_limit: `int`
    - main_state: `str`
    - main_city: `str`

    ### backup.ini

    `[default]`
    - backup_on_exit: `bool`
    - backup_places: `list`

    `[data]`
    - dbsize: `int`
    """

    def __init__(self, configname: Literal["prefs", "backup"]):
        self.config_file = path.join(CONFIG_PATH, f"{configname}.ini")
        self.log_file = path.join(LOG_PATH, f"{configname}.log")

        # config parser
        self.conf = configparser.ConfigParser()
        self.conf.read(self.config_file)
        try:
            self.conf.add_section("default")
        except configparser.DuplicateSectionError:
            pass

        # logger
        self.logger = logging.getLogger(f"cashd.{__name__}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        log_fmt = logging.Formatter("%(asctime)s :: %(levelname)s %(message)s")
        log_handler = logging.FileHandler(LOG_FILE)
        log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(log_fmt)
        self.logger.addHandler(log_handler)

        # create files, if not exist
        for file in [self.config_file, self.log_file]:
            makedirs(path.split(file)[0], exist_ok=True)
            if not path.isfile(file):
                with open(file=file, mode="a"):
                    pass

    def parse_list_from_config(self, string: str) -> list[str]:
        """
        Transforma uma config com multiplos itens uma uma lista de strings
        do python.
        """
        string = string.replace("[", "").replace("]", "")
        list_of_items = string.split(",")
        return [i.strip() for i in list_of_items if i.strip() != ""]

    def parse_list_to_config(self, list_: list[str]) -> str:
        """
        Transforma uma lista de strings do python em uma config (str) com mais
        de um item.
        """
        string_list = (
            str(list_).replace("[", "[\n\t").replace(
                ", ", ",\n\t").replace("'", "")
        )
        return string_list.replace("\\\\", "\\")

    def _write(self, sect: str, key: str, val: str):
        """Escreve a combinacao de `key` e `val` na seção `sect`"""
        try:
            if not self.conf.has_section(sect):
                self.conf.add_section(sect)

            self.conf.set(sect, key, val)
            with open(self.config_file, "w") as newconfig:
                self.conf.write(newconfig)
            self.conf.read(self.config_file)
            self.logger.info(
                f"Valor atualizado em {
                    self.config_file}: [{sect}] {key} = {val}"
            )

        except Exception as xpt:
            self.logger.error(f"Erro escrevendo [{sect}] {
                              key}={val}: {str(xpt)}")
            raise xpt

    def _read(
        self,
        sect: str,
        key: str,
        convert_to: Literal[None, "bool", "int", "list"] = None,
    ):
        try:
            if not convert_to:
                return self.conf[sect][key]
            elif convert_to == "bool":
                return self.conf.getboolean(sect, key)
            elif convert_to == "int":
                return self.conf.getint(sect, key)
            elif convert_to == "list":
                return self.parse_list_from_config(self.conf.get(sect, key))

        except KeyError:
            return None
        except configparser.NoSectionError:
            return None
        except configparser.NoOptionError:
            return None

    def _add_to_list(self, sect: str, key: str, val: str):
        if key in self.conf[sect].keys():
            current_list = self.parse_list_from_config(self.conf[sect][key])
        else:
            current_list = []
        if val in current_list:
            self.logger.warning(
                f"{val} não foi adicionado à [{sect}] {key}, item já presente."
            )
            return
        new_list = current_list + [val]

        self.conf.set(sect, key, self.parse_list_to_config(new_list))
        with open(self.config_file, "w", encoding="utf-8") as newconfig:
            self.conf.write(newconfig)
        self.conf.read(self.config_file)

    def _rm_from_list(self, sect: str, key: str, idx: int):
        """Retira o `idx`-esimo item da lista, não faz nada se `idx` for inválido."""
        try:
            idx = int(idx)
        except ValueError:
            return

        current_list = self.parse_list_from_config(self.conf[sect][key])
        n = len(current_list)

        if (idx + 1) > n:
            self.logger.error(
                f"{idx} fora dos limites, deve ser menor que {n}")

        _ = current_list.pop(idx)
        self.conf.set(sect, key, self.parse_list_to_config(current_list))
        with open(self.config_file, "w") as newconfig:
            self.conf.write(newconfig)
        self.conf.read(self.config_file, "iso 8859-1")


class PreferencesHandler(SettingsHandler):
    def __init__(self, configname="prefs"):
        super().__init__(configname)

        # set defaults
        if self.read_highest_balaces_limit() is None:
            self.write_highest_balaces_limit(10)

    def write_highest_balaces_limit(self, val: str | int):
        """
        Controla um limite de contas a ser exibidas na tabela 'Maiores saldos'.

        :raises ValueError: If `val` cannot be coerced to integer.
        :raises AttributeError: If `val` is not a string.
        """
        val = str(val)
        if not val.isnumeric():
            raise ValueError(
                f"Expected an integer or numeric string, got '{val}'.")
        self._write("default", "highest_balaces_limit", str(val))

    def read_highest_balaces_limit(self) -> int | None:
        return self._read("default", "highest_balaces_limit", convert_to="int")

    @property
    def data_tables_rows_per_page(self) -> int:
        value = self._read(
            "default", "data_tables_rows_per_page", convert_to="int")
        if not value:
            default_value = 200
            self._write("default", "data_tables_rows_per_page",
                        str(default_value))
            return default_value
        return value

    @data_tables_rows_per_page.setter
    def data_tables_rows_per_page(self, value: int):
        value = int(value)
        self._write("default", "data_tables_rows_per_page", str(value))

    @property
    def default_state(self) -> str:
        """The default state acronym displayed when creating a new customer."""
        value = self._read("default", "state")
        if not value:
            default_value = "AC"
            self._write("default", "state", default_value)
            return default_value
        return value

    @default_state.setter
    def default_state(self, value: str):
        value = value.upper()
        self._write("default", "state", value)

    @property
    def default_city(self) -> str:
        """The default city name displayed when creating a new customer."""
        value = self._read("default", "city")
        if not value:
            default_value = ""
            self._write("default", "city", default_value)
            return default_value
        return value

    @default_city.setter
    def default_city(self, value: str):
        value = value.title()
        self._write("default", "city", value)


class BackupPrefsHandler(SettingsHandler):
    def __init__(self, configname="backup"):
        super().__init__(configname)

        if self.read_backup_places() is None:
            self._write("default", "backup_places", "[]")

        if self.read_backup_on_exit() is None:
            self._write("default", "backup_on_exit", "true")

    def read_backup_places(self) -> list:
        out = self._read("default", "backup_places", convert_to="list")
        return out if out else []

    def read_backup_on_exit(self) -> bool | None:
        return self._read("default", "backup_on_exit", convert_to="bool")

    def read_dbsize(self) -> int:
        out = self._read("data", "dbsize", convert_to="int")
        return out if out else 0

    def write_dbsize(self, val: int | None) -> None:
        if val is None:
            val = 0
        else:
            val = int(val)
        self._write("data", "dbsize", str(val))

    def write_backup_on_exit(self, val: bool) -> None:
        if type(val) is not bool:
            return
        self._write("default", "backup_on_exit", "true" if val else "false")

    def add_backup_place(self, place: str) -> None:
        self._add_to_list("default", "backup_places", str(place))

    def rm_backup_place(self, idx: int) -> None:
        self._rm_from_list("default", "backup_places", idx)


###########################
# init and write defaults #
###########################

settings = PreferencesHandler()
