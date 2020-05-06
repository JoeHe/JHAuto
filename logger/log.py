import os
import sys
import logging
import logging.config as log_conf
import time

from config import config
log_dir = config.LOG_DIR
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

log_path = os.path.join(log_dir, "BI_{}.log".format(time.strftime("%Y%m%d_%H%M%S")))

log_config = {
    'version': 1.0,
    'formatters': {
        'detail': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            'format': '%(name)s - %(levelname)s - %(message)s',
        },
        'middle': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detail'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
            'filename': log_path,
            'level': config.LOG_LEVEL,
            'formatter': 'middle',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'bi_log': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    }
}

log_conf.dictConfig(log_config)

bi_logger = logging.getLogger('bi_log')

out_hdlr = logging.StreamHandler(sys.stdout)
# out_hdlr.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
out_hdlr.setLevel(config.LOG_LEVEL)

bi_logger.addHandler(out_hdlr)
bi_logger.setLevel(config.LOG_LEVEL)

