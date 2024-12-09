from __future__ import annotations
import configparser
import os
import logging
from enum import Enum
from typing import Tuple


class LogLevel(Enum):
    INFO = logging.INFO
    DEBUG = logging.DEBUG


DEFAULT_MODEM_PORT = 555
DEFAULT_PROGRAM_PORT = 5555
DEFAULT_LOG_LEVEL = LogLevel.INFO
CONFIG_PATH = "config.ini"

log = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self._ensure_config()

    def _ensure_config(self):
        if not os.path.exists(CONFIG_PATH):
            self._create_config()

    def get_ports(self) -> Tuple[int, int]:
        """
        Get port numbers from config file

        :return: Always return Tuple of (modem_port, program_port)
        """
        try:
            self.config.read(CONFIG_PATH)
            modem_port = int(self.config['PORT']["modem_port"])
            program_port = int(self.config['PORT']["program_port"])
            return modem_port, program_port
        except (KeyError, configparser.ParsingError, ValueError):
            log.error(
                f"Wrong ports, set to defaults: "
                f"modem = {DEFAULT_MODEM_PORT}, "
                f"program = {DEFAULT_PROGRAM_PORT}"
            )
        self._create_config()
        return DEFAULT_MODEM_PORT, DEFAULT_PROGRAM_PORT

    def get_log_level(self) -> int:
        """
        Get log level from config file

        :return: Log level value
        """
        try:
            self.config.read(CONFIG_PATH)
            log_level = LogLevel[self.config['LOGGER']['log_level'].upper()]
            return log_level.value
        except (KeyError, configparser.ParsingError):
            log.error(
                f"Can't find log level, set to default: "
                f"{DEFAULT_LOG_LEVEL.name}"
            )
        self._create_config()
        return DEFAULT_LOG_LEVEL.value

    @staticmethod
    def _create_config():
        """
        Create a new configuration file with default settings
        """
        config = configparser.ConfigParser()
        config['PORT'] = {
            'modem_port': str(DEFAULT_MODEM_PORT),
            'program_port': str(DEFAULT_PROGRAM_PORT)
        }
        config["LOGGER"] = {
            "log_level": DEFAULT_LOG_LEVEL.name
        }

        with open(CONFIG_PATH, 'w') as configfile:
            configfile.write("# Possible values for loglevel: DEBUG and INFO\n\n")
            config.write(configfile)
