import logging
import pathlib


logger = logging.getLogger(__name__)


BASE_DIR = pathlib.Path(__file__).parent.parent.parent
LOCAL_DIR = BASE_DIR / 'local'
LOGS_DIR = LOCAL_DIR / 'logs'

if not LOGS_DIR.is_dir():
    LOGS_DIR.mkdir(parents=True)
    logger.warning('Not found logs directory. Created, path: %s', LOGS_DIR)


DATA_PATH = BASE_DIR / 'data' / 'data.csv'
