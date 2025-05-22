import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import logfire
from datetime import datetime

# Load environment variables
load_dotenv("..")

# Create logs directory if it doesn't exist
logs_dir = Path.cwd() / ".." / "experiments" / "logs"
logs_dir.mkdir(exist_ok=True)

# Configure the logger
logger = logging.getLogger("containment")
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger (stdout)

# Configure file logging (always enabled)
timestamp = datetime.now().strftime("%Y%m%d-%H%M")
file_handler = logging.FileHandler(logs_dir / f"containment-{timestamp}.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Try to configure Logfire if token is present
logfire_token = os.getenv("LOGFIRE_WRITE_TOKEN")
if logfire_token:
    logfire.configure(token=logfire_token)
    handler = logfire.LogfireLoggingHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

logs = logger

__all__ = ["logs", "timestamp"]
