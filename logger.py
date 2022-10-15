"""Logger class for logging"""
import logging
import sys


class Logger:
    console_handler = None

    def __init__(self):
        self.logger = logging.getLogger(name="MrCrabs: ")
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(name)s: [%(asctime)s] --- %(message)s')

        self.config_console_handler()
        self.logger.addHandler(self.console_handler)

    def config_console_handler(self):
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(self.formatter)

    def get_logger(self):
        return self.logger


logger_obj = Logger()
logger = logger_obj.get_logger()
