import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import logfire
from datetime import datetime

ROOT = Path.cwd().parent
# Load environment variables
load_dotenv(ROOT / ".env")

LOGFIRE_WRITE_TOKEN = os.getenv("LOGFIRE_TOKEN")

logs_dir = ROOT / "experiments" / "logs"
logs_dir.mkdir(exist_ok=True)


def setup_logs() -> tuple[logging.Logger, str]:
    # Configure the logger
    logger = logging.getLogger("containment")
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Prevent propagation to root logger (stdout)

    # Configure file logging (always enabled)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    file_handler = logging.FileHandler(logs_dir / f"containment-{timestamp}.log")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Try to configure Logfire if token is present
    if LOGFIRE_WRITE_TOKEN:
        # import litellm

        # litellm.success_callback = ["logfire"] # BROKEN
        logfire.configure(token=LOGFIRE_WRITE_TOKEN)
        handler = logfire.LogfireLoggingHandler()
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    return logger, timestamp


logs, timestamp = setup_logs()

__all__ = ["logs", "timestamp"]
