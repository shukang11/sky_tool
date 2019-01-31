# -*- coding: utf-8 -*-
"""

@file: logging.py
@time: 2019-01-31 14:30

"""

import logging
import unittest

# create logger
logger_name = "example"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.DEBUG)

# create file handle
log_path = "./test_log.log"
file_handle = logging.FileHandler(log_path)
file_handle.setLevel(logging.WARNING)

# create formatter
formatter = "%(asctime)-15s %(levelname)s %(filename)s %(lineno)d %(process)d %(message)s"
date_formatter = "%a %d %b %Y %H:%M:%S"
formatter = logging.Formatter(formatter, date_formatter)

# add handler and formatter to logger
file_handle.setFormatter(formatter)
logger.addHandler(file_handle)


class test_logging(unittest.TestCase):

    def test_begin(self):
        print("begin test")
        self.assertEqual(1,2)

    def test_log(self):
        print("test_log")
        logger.debug("debuge message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")
        self.assertEqual(1, 1)

if __name__ == "__main__":
    logger.debug("debuge message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")