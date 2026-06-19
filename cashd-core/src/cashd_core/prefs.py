from os import path, makedirs
from sys import platform
from pathlib import Path
from typing import Literal, Iterator, Any, Callable
from configparser import (
    ConfigParser,
    NoOptionError,
    NoSectionError,
    DuplicateOptionError,
    DuplicateSectionError,
)
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


def get_parser(filename: str) -> tuple[Path, ConfigParser]:
    """Base function to produce *parser factories*. The parser factories should not
    take any input value, and return a `ConfigParser`.

    :filename: Name of the config file without extension.

    :returns: A tuple with two items, in order: 1- A `Path` object describing the
      config file location; 2- A `ConfigParser`.
    """
    parser = ConfigParser()
    config_file = Path(CONFIG_PATH, f"{filename}.ini")
    config_file.touch(exist_ok=True)
    parser.read(config_file)
    return (config_file, parser)


def prefs_parser():
    """Factory of parsers for the 'prefs.ini' config file."""
    return get_parser(filename="prefs")


def backup_parser():
    """Factory of parser for ther 'backup.ini' config file."""
    return get_parser(filename="backup")


class _Config:
    def __init__(
        self,
        key: str,
        default: Any,
        parser_factory: Callable[[], tuple[Path, ConfigParser]] = prefs_parser,
        section: str = "default",
    ):
        """Base class that sets logic for interacting with a key that returns a
        single value on a specific configuration file.

        :parser_factory: Function that always returns a `ConfigParser` with an attribute
          `_config_file` indicating the file to where this parser writes.
        :section: Name of the section where this config is located.
        :key: Name of this option in the config file.
        :default: Default value of this option, must be compatible with the input type
          of this class' `__set` method.
        """
        self._parser_factory, self._section, self._key, self._default = (
            parser_factory,
            section,
            key,
            default,
        )

        config_file, parser = self._parser_factory()
        if not parser.has_section(section):
            parser.add_section(section=section)
            with open(config_file, "w") as configfile:
                parser.write(configfile)

        self.logger = logging.getLogger(f"cashd.{__name__}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False

        log_fmt = logging.Formatter("%(asctime)s :: %(levelname)s %(message)s")
        log_handler = logging.FileHandler(LOG_FILE)
        log_handler.setLevel(logging.DEBUG)
        log_handler.setFormatter(log_fmt)
        self.logger.addHandler(log_handler)

    @classmethod
    def get(cls):
        """Get current value of this config, or the default value if not defined."""
        interactor = cls()
        return interactor.__get()

    @classmethod
    def set(cls, value: Any):
        """Write `value` to the configuration file."""
        interactor = cls()
        interactor.__set(value)

    def __set(self, value: Any):
        config_file, parser = self._parser_factory()
        parser.set(self._section, self._key, str(value))
        try:
            with open(config_file, "w") as buffer:
                parser.write(buffer)
        except Exception as err:
            self.logger.error(
                f"Unexpected error trying set {self._key}={value} on "
                f"{config_file.name}[{self._section}], {err}"
            )
            raise
        else:
            self.logger.info(
                f"Config updated {self._key}={value} on {config_file.name}"
                f"[{self._section}]"
            )

    def __get(self) -> Any | None:
        config_file, parser = self._parser_factory()
        try:
            return parser.get(self._section, self._key, fallback=self._default)
        except NoOptionError:
            self.logger.info(
                f"Could not find option {self._key} on {config_file.name}"
                f'[{self._section}], writing option with default "{self._default}"'
            )
            self.__set(value=str(self._default))
            return self._default
        except Exception as err:
            self.logger.error(
                f"Unexpected error getting {self._key} from {config_file.name}"
                f"[{self._section}], {err}"
            )
            raise


class _ConfigList(_Config):
    """Wrapper base class for configs that handle lists of strings."""

    @classmethod
    def get(cls) -> list[str]:
        """Get list from config file as a python list."""
        interactor = cls()
        return list(interactor.__get())

    @classmethod
    def set(cls, value: list[str]):
        """Writes a a python list to the config file, replacing the existing one."""
        interactor = cls()
        interactor.__set(value=[str(i) for i in value])

    @classmethod
    def add(cls, value: str):
        """Adds a `value` to the config list."""
        interactor = cls()
        interactor.__add(value=value)

    @classmethod
    def rm(cls, value: str):
        """Removes `value` from config list if it is present. Does nothing otherwise."""
        interactor = cls()
        interactor.__rm(value=value)

    def __get(self) -> Iterator[str]:
        config_file, parser = self._parser_factory()
        try:
            string = parser.get(self._section, self._key)
            string = string.replace("[", "").replace("]", "")
            list_of_items = string.split(",")
        except NoOptionError:
            self.logger.info(
                f"Could not find option {self._key} on {config_file.name}"
                f'[{self._section}], writing option with default "{self._default}"'
            )
            self.__set(value=self._default)
            list_of_items = self._default
        except Exception as err:
            self.logger.error(
                f"Unexpected error getting {self._key} from {config_file.name}"
                f"[{self._section}], {err}"
            )
            raise
        return (i.strip() for i in list_of_items if i.strip() != "")

    def __set(self, value: list[str]):
        string_list = (
            str(value)
            .replace("[", "[\n\t")
            .replace(", ", ",\n\t")
            .replace("'", "")
            .replace("]", "\n]")
            .replace("\\\\", "\\")
        )
        config_file, parser = self._parser_factory()
        parser.set(self._section, self._key, string_list)
        try:
            with open(config_file, "w") as configfile:
                parser.write(configfile)
        except Exception as err:
            self.logger.error(
                f"Unexpected error trying set {self._key}={value} on "
                f"{config_file.name}[{self._section}], {err}"
            )
            raise
        else:
            self.logger.info(
                f"Config updated {self._key}={value} on {config_file.name}"
                f"[{self._section}]"
            )

    def __add(self, value: str):
        current = [i for i in self.__get()]
        new = current + [value]
        self.__set(value=new)

    def __rm(self, value: str):
        current = [i for i in self.__get()]
        try:
            current.remove(value)
        except ValueError:
            return
        self.__set(value=current)


class _ConfigInt(_Config):
    """Wrapper base class for configs that handle integer values."""

    @classmethod
    def get(cls):
        value = super().get()
        return int(value)


class _ConfigBool(_Config):
    """Wrapper base class for configs that handle boolean values."""

    @classmethod
    def get(cls) -> bool:
        value = super().get()
        return value == "true"

    @classmethod
    def set(cls, value: bool):
        if type(value) is not bool:
            raise ValueError(f"Value must be of type {bool}, not {type(value)}")
        new_value = str(value).lower()
        super().set(value=new_value)


# prefs.ini


class DefaultState(_Config):
    def __init__(self):
        super().__init__(key="state", default="AC")


class DefaultCity(_Config):
    def __init__(self):
        super().__init__(key="city", default="")


class RowsPerPage(_ConfigInt):
    def __init__(self):
        super().__init__(key="rows_per_page", default="200")


class AreaCodeNumber(_ConfigInt):
    def __init__(self):
        super().__init__(key="area_code_number", default="99")


# backup.ini


class BackupPlaces(_ConfigList):
    def __init__(self):
        super().__init__(parser_factory=backup_parser, key="backup_places", default=[])


class DBSize(_ConfigInt):
    def __init__(self):
        super().__init__(parser_factory=backup_parser, key="dbsize", default=0)


class BackupOnClose(_ConfigBool):
    def __init__(self):
        super().__init__(
            parser_factory=backup_parser, key="backup_on_close", default=False
        )


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
        self.conf = ConfigParser()
        self.conf.read(self.config_file)
        try:
            self.conf.add_section("default")
        except DuplicateSectionError:
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
            str(list_).replace("[", "[\n\t").replace(", ", ",\n\t").replace("'", "")
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
            self.logger.error(
                f"Erro escrevendo [{sect}] {
                              key}={val}: {str(xpt)}"
            )
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
        except NoSectionError:
            return None
        except NoOptionError:
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
            self.logger.error(f"{idx} fora dos limites, deve ser menor que {n}")

        _ = current_list.pop(idx)
        self.conf.set(sect, key, self.parse_list_to_config(current_list))
        with open(self.config_file, "w") as newconfig:
            self.conf.write(newconfig)
        self.conf.read(self.config_file, "iso 8859-1")


class PreferencesHandler(SettingsHandler):
    def __init__(self, configname="prefs"):
        super().__init__(configname)

    @property
    def data_tables_rows_per_page(self) -> int:
        value = self._read("default", "data_tables_rows_per_page", convert_to="int")
        if not value:
            default_value = 200
            self._write("default", "data_tables_rows_per_page", str(default_value))
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

    @property
    def area_code_number(self) -> int:
        """The default first two digits displayed in the 'phone number' field when
        creating a new customer.
        """
        value = self._read("default", "area_code_number", convert_to="int")
        if value is None:
            default_value = "99"
            self._write("default", "area_code_number", default_value)
            return default_value
        return value

    @area_code_number.setter
    def area_code_number(self, value: int):
        value = int(value)
        self._write("default", "area_code_number", str(value))


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
