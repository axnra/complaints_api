from loguru import logger
import sys
from pathlib import Path

# Define the directory where log files will be stored
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


# Remove the default Loguru handler
logger.remove()


# Add a console handler with colored output and detailed format
logger.add(
    sys.stdout,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>"
)

# Add a file handler with rotation, compression, and retention
logger.add(
    LOG_DIR / "app.log",
    rotation="10 MB",               # Rotate log file after 10 MB
    retention="10 days",            # Keep logs for 10 days
    compression="zip",              # Compress old logs
    level="INFO",                   # Only log INFO and higher to file
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    enqueue=True,                   # Makes it safe for multiprocess logging
    backtrace=True,                 # Enables detailed tracebacks
    diagnose=True                   # Enables variable inspection in exceptions
)
