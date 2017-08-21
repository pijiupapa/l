import logging
import logging.config


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },

        # "info_file":{
        #     "class": "logging.FileHandler",
        #     "level": "INFO",
        #     "formatter": "simple",
        #     "filename": "log/colla.log"
        # },
        #
        # "error_file":{
        #     "class": "logging.FileHandler",
        #     "level": "ERROR",
        #     "formatter": "simple",
        #     "filename": "log/colla_error.log"
        # },
    },

    'loggers': {
        'adsl': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


logging.config.dictConfig(LOGGING)

logger = logging.getLogger('adsl')
