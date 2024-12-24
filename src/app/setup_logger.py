import logging
from datetime import datetime
import os
from .config_manager import ConfigManager


def setup_logger():
    logfile_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log'
    logfile_path = os.path.join('logs', logfile_name)
    os.makedirs(os.path.dirname(logfile_path), exist_ok=True)

    config = ConfigManager()
    level = config.get_log_level()

    logging.basicConfig(
        format='%(asctime)s|%(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=level,
        handlers=[
            logging.FileHandler(logfile_path),
            logging.StreamHandler()
        ]
    )


