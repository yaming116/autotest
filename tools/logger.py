# !/usr/bin/env python

import logging
import sys
import socket
import os


def setup_logger(level=logging.NOTSET):
    logger.propagate = False
    date_format = '%Y-%m-%d %H:%M:%S'
    host_name = socket.gethostname()
    formater = '[%(asctime)s] [%(levelname)s] [' + host_name + '][%(module)s.py - line:%(lineno)d] %(message)s'
    logging.basicConfig(level=level, format=formater, datefmt=date_format)
    # console
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter(formater))
    logger.addHandler(handler)
    # file
    from config import case_logs
    if not os.path.exists(case_logs):
        os.makedirs(case_logs)
    log_file = os.path.join(case_logs, 'system.log')

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(formater))
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)


# global logger
logger = logging.getLogger(__name__)
setup_logger()
