"""Bounded runtime logging and uncaught-exception hooks."""

import asyncio
import datetime
import faulthandler
import logging
import os
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import IO

from project_paths import LOG_DIR


LOGGER_NAME = "tincanargentum"
LOG_FILE = LOG_DIR / "bot.log"
FATAL_LOG_FILE = LOG_DIR / "fatal.log"
SESSION_FILE = LOG_DIR / "running.lock"
MAX_LOG_BYTES = 2 * 1024 * 1024
BACKUP_COUNT = 3
_HANDLER_MARKER = "_tincan_runtime_handler"
_fatal_stream: IO[str] | None = None


def _rotate_fatal_log(path: Path) -> None:
    if path.exists() and path.stat().st_size >= MAX_LOG_BYTES:
        backup = path.with_suffix(".log.1")
        backup.unlink(missing_ok=True)
        path.replace(backup)


def configure_runtime_logging() -> logging.Logger:
    """Configure one process-wide, size-limited UTF-8 file handler."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger()
    if not any(
        getattr(handler, _HANDLER_MARKER, False)
        for handler in root_logger.handlers
    ):
        handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_LOG_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
            delay=True,
        )
        setattr(handler, _HANDLER_MARKER, True)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | "
                "%(threadName)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        root_logger.addHandler(handler)
    if root_logger.level == logging.NOTSET or root_logger.level > logging.INFO:
        root_logger.setLevel(logging.INFO)

    # These libraries can otherwise fill the bounded log with request details.
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    return logging.getLogger(LOGGER_NAME)


def install_exception_hooks(logger: logging.Logger) -> None:
    """Log uncaught main-thread, worker-thread, and fatal Python errors."""
    original_sys_hook = sys.excepthook

    def sys_hook(exc_type, exc_value, traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            original_sys_hook(exc_type, exc_value, traceback)
            return
        logger.critical(
            "Uncaught main-thread exception",
            exc_info=(exc_type, exc_value, traceback),
        )

    def thread_hook(args: threading.ExceptHookArgs):
        if args.exc_type is SystemExit:
            return
        logger.critical(
            "Uncaught thread exception: %s",
            args.thread.name if args.thread else "unknown",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.excepthook = sys_hook
    threading.excepthook = thread_hook

    global _fatal_stream
    if _fatal_stream is None:
        _rotate_fatal_log(FATAL_LOG_FILE)
        _fatal_stream = FATAL_LOG_FILE.open("a", encoding="utf-8")
        faulthandler.enable(file=_fatal_stream, all_threads=True)


def mark_runtime_start(logger: logging.Logger) -> None:
    """Leave a marker that reveals a previous hard or unclean shutdown."""
    if SESSION_FILE.exists():
        previous = SESSION_FILE.read_text(encoding="utf-8", errors="replace").strip()
        logger.warning(
            "Previous process did not shut down cleanly | marker=%s",
            previous or "empty",
        )
    marker = (
        f"pid={os.getpid()} "
        f"started_at={datetime.datetime.now(datetime.timezone.utc).isoformat()}"
    )
    SESSION_FILE.write_text(marker, encoding="utf-8")


def install_asyncio_exception_handler(
    loop: asyncio.AbstractEventLoop,
    logger: logging.Logger,
) -> None:
    """Log exceptions from tasks that nobody awaited."""

    def handle_exception(
        active_loop: asyncio.AbstractEventLoop,
        context: dict,
    ) -> None:
        exception = context.get("exception")
        message = context.get("message", "Unhandled asyncio exception")
        if exception is None:
            logger.error("%s | context=%r", message, context)
        else:
            logger.error(
                "%s",
                message,
                exc_info=(
                    type(exception),
                    exception,
                    exception.__traceback__,
                ),
            )
        active_loop.default_exception_handler(context)

    loop.set_exception_handler(handle_exception)


def close_runtime_logging() -> None:
    """Flush logs and close the fatal-error stream during process shutdown."""
    SESSION_FILE.unlink(missing_ok=True)
    logging.shutdown()
    global _fatal_stream
    if _fatal_stream is not None:
        faulthandler.disable()
        _fatal_stream.close()
        _fatal_stream = None
