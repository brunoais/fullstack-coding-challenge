import logging
from collections import UserList
from functools import partial

import config

LOG = logging.getLogger("boot_queue." + config.LOG_BASE_NAME + '.' + __name__)


class BootQueue(UserList):
    def __init__(self, initlist=None):
        self.data = []  # to pass on the data attr IDE inspection
        initlist = initlist or []
        super().__init__(initlist)

    def add(self, function, *args, **kwargs):
        """ Add a function to be run at end of server startup"""
        if callable(function):
            self.data.append((function, args, kwargs))
        else:
            def decorated(function):
                self.data.append((function, args, kwargs))
            return decorated

    def run_startup_tasks(self):
        for func, args, kwargs in self.data:
            try:
                try:
                    LOG.info("running %s(%s, %s)", func.__name__, ', '.join(map(str, args)), ', '.join(key + "=" + str(val) for key, val in kwargs.items()))
                except Exception:
                    LOG.info("running %s(...)", func.__name__)

                func(*args, *kwargs)
            except Exception:
                LOG.error("%s, failed. Aborting", func.__name__)
                raise
            else:
                LOG.info("%s, success", func.__name__)

boot_queue = BootQueue()

