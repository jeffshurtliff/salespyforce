import logging
import sys

import pytest

from salespyforce.utils import log_utils


def _cleanup_logger(logger: logging.Logger) -> None:
    """Remove and close handlers for a logger.

    :param logger: The logger instance to clean up.
    """
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()


def test_initialize_logging_defaults_to_info_level() -> None:
    """Verify initialize_logging defaults logger level to INFO."""
    logger_name = "salespyforce.test.default.info"
    logger = log_utils.initialize_logging(logger_name)
    try:
        assert logger.level == logging.INFO
    finally:
        _cleanup_logger(logger)


def test_initialize_logging_applies_default_level_to_console_handler(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Ensure console handlers inherit the default INFO level.

    :param caplog: Pytest fixture capturing log records for assertions.
    """
    logger_name = "salespyforce.test.console.default"
    logger = log_utils.initialize_logging(logger_name, console_output=True)
    message = "default info message"
    try:
        with caplog.at_level(logging.INFO, logger=logger_name):
            logger.info(message)

        stdout_handlers = [
            handler
            for handler in logger.handlers
            if isinstance(handler, logging.StreamHandler)
            and getattr(handler, "stream", None) is sys.stdout
        ]
        assert stdout_handlers
        for handler in stdout_handlers:
            assert handler.level == logging.INFO

        assert any(
            record.levelno == logging.INFO and record.message == message
            for record in caplog.records
        )
    finally:
        _cleanup_logger(logger)
