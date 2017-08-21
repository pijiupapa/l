import logging
import logging.config


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(msg)s",
            # "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },

        "info_file":{
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "log/core.log"
        },

        "error_file":{
            "class": "logging.FileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename": "log/error.log"
        },
    },

    'loggers': {
        'core': {
            'handlers': ["console", "info_file", "error_file"],
            'level': logging.DEBUG,
            'propagate': True,
        },
    },
}


# logging.config.dictConfig(LOGGING)

logger = logging.getLogger('core')
