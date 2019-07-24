from os import environ

from .paths import LOGS_DIR

DISABLE_CONSOLE_LOG = environ.get('DISABLE_CONSOLE_LOG', str(True)) == str(True)

LOGGING_CONF = {
    'disable_existing_loggers': True,
    'version': 1,
    'formatters': {'verbose': {'format': '%(levelname)-8s %(asctime)s [%(filename)s:%(lineno)d] %(message)s'}},
    'handlers': {
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'verbose'},
        'app_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'filename': LOGS_DIR / 'app.log',
            'backupCount': 30,
            'when': 'midnight',
            'interval': 1,
            'utc': True,
        },
    },
    'loggers': {
        'app': {'level': 'INFO', 'handlers': ['app_file'] if DISABLE_CONSOLE_LOG else ['console', 'app_file']},
        'aiohttp': {'level': 'INFO', 'handlers': ['app_file'] if DISABLE_CONSOLE_LOG else ['console', 'app_file']},
        'asyncio': {'level': 'INFO', 'handlers': ['app_file'] if DISABLE_CONSOLE_LOG else ['console', 'app_file']},
    },
}
