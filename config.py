
import enum
import logging
import os
import random
import sys
from collections import namedtuple

from logging import handlers
from os import path


UNBABEL_USERNAME = os.environ.get('UNBABEL_USERNAME', 'fullstack-challenge')
UNBABEL_API_KEY = os.environ['UNBABEL_API_KEY']

VALID_SOURCE_LANGUAGES = set(('en',))  # Can be evolved to make use of environ variables
VALID_TARGET_LANGUAGES = set(('es',))

UPDATE_TRANSLATIONS_POLL_INTERVAL_SECS = float(os.environ.get('UPDATE_TRANSLATIONS_POLL_INTERVAL_SECS', '5'))


OBDC_SERVER_NAME = os.environ.get('OBDC_SERVER_NAME', 'localhost')

ODBC_CONN_STR = (
    "DRIVER={PostgreSQL Unicode};"
    "DATABASE=user;"
    "UID=user;"
    "PWD=testingpassword;"
    "SERVER=" + OBDC_SERVER_NAME + ";"
    "PORT=5432;"
)

UNIT_TESTS = False


LOG_FORMAT = os.environ.get('LOG_FORMAT', "%(asctime)-15s @%(threadName)s [%(levelname)-5.5s] %(funcName)s() (%(request_id)s) %(message)s")
LOG_EXEC_ENV = os.environ.get('LOG_EXEC_ENV', "DEV")
LOG_FILE_NAME = os.environ.get('LOG_FILE_NAME', os.path.basename(sys.argv[0]))
LOG_LOCATION = os.environ.get('LOG_LOCATION', "./logs")
LOG_LOCATION_VERBOSE = os.environ.get('LOG_LOCATION_VERBOSE', LOG_LOCATION)
LOG_BACKUP_ROTATE_SIZE_KB = int(os.environ.get('LOG_BACKUP_ROTATE_SIZE_KB', "4096")) * 1024
LOG_BACKUP_COUNT_NORMAL = int(os.environ.get('LOG_BACKUP_COUNT_NORMAL', "5"))
LOG_BACKUP_COUNT_VERBOSE = int(os.environ.get('LOG_BACKUP_COUNT_VERBOSE', str(int(LOG_BACKUP_COUNT_NORMAL) * 2) ))
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_CONSOLE_DEACTIVATE = os.environ.get('LOG_CONSOLE_DEACTIVATE', None)
LOG_BASE_NAME = os.environ.get('LOG_BASE_NAME', "dd.review")

# Do all on the app root logger. All other loggers must work on top of this one
LOG = logging.getLogger(LOG_BASE_NAME)
LOG.setLevel(logging.DEBUG)
logFormat = logging.Formatter(LOG_FORMAT)

LOG_health = logging.getLogger('health_check.' + LOG_BASE_NAME)
LOG_health.setLevel(logging.DEBUG)

LOG_static = logging.getLogger('static_files.' + LOG_BASE_NAME)
LOG_static.setLevel(logging.DEBUG)
static_logFormat = logging.Formatter('STATIC: ' + LOG_FORMAT)

# libraries

socketio_log = logging.getLogger('engineio.server')
socketio_log.setLevel(logging.DEBUG)

os.makedirs(LOG_LOCATION, exist_ok=True)

logFileHandler = handlers.RotatingFileHandler(path.normpath(LOG_LOCATION + "/{0}.log".format(LOG_FILE_NAME)), maxBytes=LOG_BACKUP_ROTATE_SIZE_KB, backupCount=int(LOG_BACKUP_COUNT_NORMAL), encoding='utf-8')
logFileHandler.setLevel(LOG_LEVEL)
logFileHandler.setFormatter(logFormat)
LOG.addHandler(logFileHandler)

if LOG_LOCATION_VERBOSE:
    logVerboseFileHandler = handlers.RotatingFileHandler(path.normpath(LOG_LOCATION_VERBOSE + "/{0}.verbose.log".format(LOG_FILE_NAME)), maxBytes=LOG_BACKUP_ROTATE_SIZE_KB, backupCount=int(LOG_BACKUP_COUNT_VERBOSE), encoding='utf-8')
    logVerboseFileHandler.setLevel(logging.DEBUG)
    logVerboseFileHandler.setFormatter(logFormat)
    LOG.addHandler(logVerboseFileHandler)


if not LOG_CONSOLE_DEACTIVATE:
    logConsoleHandler = logging.StreamHandler()
    logConsoleHandler.setFormatter(logFormat)
    logConsoleHandler.setLevel(logging.INFO)
    LOG.addHandler(logConsoleHandler)
    
    static_logConsoleHandler = logging.StreamHandler()
    static_logConsoleHandler.setFormatter(static_logFormat)
    static_logConsoleHandler.setLevel(logging.INFO)
    LOG_static.addHandler(static_logConsoleHandler)
    


import shared.flask
shared.flask.request_id_in_logs()

LOG.warning("\n\n")
LOG.warning("-------LOG STARTING FOR %s on env %s -------\n\n", LOG_FILE_NAME, LOG_EXEC_ENV)


from shared.global_enums import StrEnum
class LoginMessages(StrEnum):
    NONE = enum.auto()
    LOGIN_REQUIRED = enum.auto()
    WRONG_CREDENTIALS = enum.auto()
    REAUTH_NEEDED = enum.auto()
    INVALID_TOKEN = enum.auto()
    SESSION_TIMEOUT = enum.auto()

