import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

from logis._log import LoggerBuilder


def test_logger_builder():
    log = (
        LoggerBuilder()
        .name("test_logger")
        .level(logging.INFO)
        .add_handler(StreamHandler)
        .add_handler(RotatingFileHandler, file_name="test")
        .build()
    )
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message")
    log.exception("This is an exception message")


if __name__ == "__main__":
    test_logger_builder()
