import os, datetime
from .helpers import *

DEVELOPMENT = 0
TEST = 1
PRODUCTION = 2
environments = ['DEVELOPMENT', 'TEST', 'PRODUCTION']

DEBUG = 0
INFO = 1
WARN = 2
FATAL = 3

log_levels = ['DEBUG', 'INFO', 'WARN', 'FATAL']

class Logger():

    def __init__(self, **kwargs):
        self.config = updateConfig({
            'application': 'LOGGER',
            'log_level': DEBUG,
            'environment': PRODUCTION,
            'log_path': os.getcwd()
        }, kwargs)

        self.output_path = os.path.join(
            self.config['log_path'],
            str(environments[PRODUCTION]) + ".log"
        )

        if os.path.exists(self.output_path):
            open_option = 'a'
        else:
            open_option = 'w'

        with open(self.output_path, open_option) as f:
            f.write(self.getEntryLine(INFO, 'Logger Initialized'))
            f.close()

    def getEntryLine(self, level, msg):
        return (
            "[%s][%s] %s -- %s" % (
                self.config['application'],
                str(datetime.datetime.now()),
                log_levels[level],
                msg
            )
        )

    def log(self, level, msg):
        if (level >= self.config['log_level']):
            log_line = self.getEntryLine(level, msg)
            print(log_line)

            with open(self.output_path, 'a') as f:
                f.write(log_line)
                f.close()
