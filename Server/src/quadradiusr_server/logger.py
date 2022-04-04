
import logging.config


def configure_logger(verbosity: int):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'class': 'logging.Formatter',
                'format': '[{asctime}.{msecs:3.0f}] {levelname} {message}',
                'style': '{',
                'datefmt': '%H:%M:%S',
            },
            'verbose': {
                'class': 'logging.Formatter',
                'format': '{asctime} {threadName:10} [{name:24}] {levelname:7} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG' if verbosity > 0 else 'INFO',
                'formatter': 'verbose' if verbosity > 0 else 'standard',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'DEBUG',
            },
            'aiohttp.access': {
                'handlers': ['default'],
                'level': 'DEBUG',
            },
            'aiosqlite': {
                'handlers': ['default'],
                'level': 'DEBUG' if verbosity > 1 else 'INFO',
            },
            'aiohttp.client': {
                'handlers': ['default'],
                'level': 'DEBUG',
            },
            'aiohttp.internal': {
                'handlers': ['default'],
                'level': 'DEBUG',
            },
            'aiohttp.server': {
                'handlers': ['default'],
                'level': 'DEBUG',
            },
            'aiohttp.web': {
                'handlers': ['default'],
                'level': 'DEBUG',
            },
            'aiohttp.websocket': {
                'handlers': ['default'],
                'level': 'DEBUG',
            },
        },
    })
