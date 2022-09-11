#!/usr/bin/python3
# -*- coding: utf8 -*-

import logging
import os.path
import sys
from logging.handlers import RotatingFileHandler

from config import *


def init_logging():
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s')
    log_file = os.path.join(LOG_DIR, "bing.log")

    file_hdl = RotatingFileHandler(log_file, maxBytes=100 * 1024 * 1024, backupCount=10)
    file_hdl.setFormatter(formatter)
    stdout_hdl = logging.StreamHandler(sys.stdout)
    stdout_hdl.setFormatter(formatter)

    logger.addHandler(file_hdl)
    logger.addHandler(stdout_hdl)
    logger.setLevel(logging.INFO)


init_logging()

logger = logging.getLogger()

if __name__ == '__main__':
    logger.error("[logger] error")
    logger.warning("[logger] waring")
    logger.info("[logger] info")
