from logging.handlers import RotatingFileHandler
from pathlib import Path
import logging
from api.core.config import AppConfig


def setup_logger(appConfig:  AppConfig) -> logging.Logger:
    """
    Configure the logger for the MeasurementsApp.

    Sets the log level to INFO and defines a formatter for the log messages.
    Creates a directory called "logs" if it doesn't exist already.
    Creates two rotating file handlers, one for the "app.log" file and another for the "error.log" file.
    Configures the file handlers with a maximum file size of 1MB and a backup count of 5.
    Creates a console handler and adds it to the logger.
    Adds the file handlers to the logger.
    Returns the configured logger.
    """
    logger = logging.getLogger("MeasurementsApp")

    logger.setLevel(appConfig.app_loglevel)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    log_directory = Path("logs")
    log_directory.mkdir(parents=True, exist_ok=True)

    log_file1 = log_directory / "app.log"
    file_handler1 = RotatingFileHandler(
        log_file1, maxBytes=1000000, backupCount=5)
    file_handler1.setFormatter(formatter)

    log_file2 = log_directory / "error.log"
    file_handler2 = RotatingFileHandler(
        log_file2, maxBytes=1000000, backupCount=5)
    file_handler2.setLevel(logging.ERROR)
    file_handler2.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler1)
    logger.addHandler(file_handler2)
    return logger
