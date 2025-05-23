import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import logfire
from datetime import datetime

ROOT = Path.cwd().parent
logs_dir = ROOT / "experiments" / "logs"

load_dotenv(ROOT / ".env")

LOGFIRE_WRITE_TOKEN = os.getenv("LOGFIRE_TOKEN")

logs_dir.mkdir(exist_ok=True)


def _script_name() -> str:
    """
    Get the script name from the command line arguments.
    """
    if len(sys.argv) > 1:
        return f"{Path(sys.argv[0]).stem}_{sys.argv[1]}"
    return Path(sys.argv[0]).stem


class LoggerSetup:
    """Singleton class to set up logging for the script, ensuring it's run once."""

    _instance = None
    _logger = None
    _timestamp = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_logger(self):
        if self._logger is None:
            self._logger, self._timestamp = self._setup_logs()
        return self._logger

    def get_timestamp(self):
        if self._timestamp is None:
            self._logger, self._timestamp = self._setup_logs()
        return self._timestamp

    def _setup_logs(self):
        # Configure the logger
        script_name = _script_name()
        logger = logging.getLogger(script_name)
        logger.setLevel(logging.INFO)
        # logger.propagate = False  # Prevent propagation to root logger (stdout)

        # Configure file logging (always enabled)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        file_handler = logging.FileHandler(logs_dir / f"{script_name}_{timestamp}.log")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s - %(name)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Try to configure Logfire if token is present
        if LOGFIRE_WRITE_TOKEN:
            import litellm

            litellm.callbacks = ["logfire"]  # forces mcp to 1.5
            logfire.configure(token=LOGFIRE_WRITE_TOKEN)
            handler = logfire.LogfireLoggingHandler()
            handler.setLevel(logging.INFO)
            logger.addHandler(handler)

        return logger, timestamp


_setup = LoggerSetup()
logs = _setup.get_logger()
timestamp = _setup.get_timestamp()
