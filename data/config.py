import os
import sys
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

if getattr(sys, "frozen", False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()

FILES_DIR = os.path.join(ROOT_DIR, "files")
ABIS_DIR = os.path.join(ROOT_DIR, "abis")


PROXY_FILE = os.path.join(FILES_DIR, "proxy.txt")
PRIVATE_FILE = os.path.join(FILES_DIR, "private.txt")
ENV_FILE = os.path.join(ROOT_DIR, ".env")

RESERVE_PROXY_FILE = os.path.join(FILES_DIR, "reserve_proxy.txt")

SETTINGS_FILE = os.path.join(FILES_DIR, "settings.json")
LOG_FILE = os.path.join(FILES_DIR, "log.log")
ERRORS_FILE = os.path.join(FILES_DIR, "errors.log")

logger.add(ERRORS_FILE, level="ERROR")
logger.add(LOG_FILE, level="INFO")
