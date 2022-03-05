
import os
import logging

from .settings import BASE_DIR

level = 'DEBUG'
__all__ = ['LOGGING']

log_folder = os.path.join(BASE_DIR, 'logs')
logger = logging.getLogger(__name__)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S",
        },
        'standard_testing': {
            'format': "%(levelname)s [%(name)s]:%(lineno)s: %(message)s",
        },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
        'timestampthread': {
            'format': "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-20.20s]  %(message)s",
        },
    },

    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(log_folder, 'log'),
            'maxBytes': 50000,
            'backupCount': 3,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'test': {
            'level': 'DEBUG',
            # 'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard_testing',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['console'],
            # 'handlers': ['logfile', 'console'],
            'propagate': False,
            'level': 'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARN',
            'propagate': False,
        },
        'config': {
            'handlers': ['test'],
            'level': level,
            'propagate': True,
        },
        'staff': {
            'handlers': ['test'],
            'level': 'DEBUG',
            'propagate': True,
        },

        'trackr': {
            'handlers': ['test'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'sitemgr': {
            'handlers': ['test'],
            'level': 'DEBUG',
            'propagate': True,
        },

        'filemgr': {
            'handlers': ['test'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}


config = logging.config.dictConfig(LOGGING)
