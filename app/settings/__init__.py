from .settings import *
from .logging_config import LOGGING_CONF
from .paths import DATA_PATH, DOCS_PATH
import logging.config

logging.config.dictConfig(LOGGING_CONF)
