#!/usr/bin/python3
# -*- coding: utf8 -*-

import logging
import os.path
import sys
from logging.handlers import RotatingFileHandler


def init_logging(filelog: bool, path: str):
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d %(message)s')

    if filelog:
        if not os.path.exists(path):
            os.makedirs(path)
        log_file = os.path.join(path, "bing.log")
        file_hdl = RotatingFileHandler(log_file, maxBytes=100 * 1024 * 1024, backupCount=10)
        file_hdl.setFormatter(formatter)
        logger.addHandler(file_hdl)

    stdout_hdl = logging.StreamHandler(sys.stdout)
    stdout_hdl.setFormatter(formatter)

    logger.addHandler(stdout_hdl)
    logger.setLevel(logging.INFO)


if __name__ == '__main__':
    init_logging(True, ".")
    logging.error("[logger] error")
    logging.warning("[logger] waring")
    logging.info("[logger] info")
