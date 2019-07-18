LOGGING_CONF = {
    'disable_existing_loggers': True,
    'version': 1,
    'formatters': {'verbose': {'format': '%(levelname)-8s %(asctime)s [%(filename)s:%(lineno)d] %(message)s'}},
    'handlers': {'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'verbose'}},
    'loggers': {
        'app': {'level': 'INFO', 'handlers': ['console']},
        'asyncio': {'level': 'INFO', 'handlers': ['console']},
    },
}
