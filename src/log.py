#!/usr/bin/python3
# -*- coding: utf8 -*-

import logging
import os.path
import sys
from logging.handlers import RotatingFileHandler


def init_logging(log_path: str, log_level: str):
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s')

    if not log_path or len(log_path) == 0:
        stdout_hdl = logging.StreamHandler(sys.stdout)
        stdout_hdl.setFormatter(formatter)
        logger.addHandler(stdout_hdl)
    else:
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        log_file = os.path.join(log_path, "bing.log")
        file_hdl = RotatingFileHandler(log_file, maxBytes=100 * 1024 * 1024, backupCount=10)
        file_hdl.setFormatter(formatter)
        logger.addHandler(file_hdl)

    level = logging.getLevelName(log_level)
    logger.setLevel(level)


if __name__ == '__main__':
    init_logging("", "WARNING")
    logging.error("[logger] error")
    logging.warning("[logger] waring")
    logging.info("[logger] info")
