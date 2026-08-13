"""Centralized logging utility for SAMS Vision."""

import logging
import sys

# Default Windows consoles (cmd.exe / legacy PowerShell) use a non-UTF-8 codepage with strict
# error handling, which raises UnicodeEncodeError and crashes the process the moment a message
# contains a character like an em dash or emoji. Reconfiguring stdout/stderr to UTF-8 with a
# replace fallback means those characters render correctly where the console supports it, and
# degrade to a harmless '?' instead of crashing where it doesn't.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, AttributeError):
            pass


def setup_logger(name: str = "sams_vision", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a logger instance with standardized formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
