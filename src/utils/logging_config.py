from datetime import datetime
import logging.config
import os
from typing import Dict, Any


def setup_logging():
    """Setup logging configuration"""
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            },
        },
        "root": {
            "level": "INFO",
            "handlers": ["default"]
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)