import logging

from flask import g, render_template

import config

LOG = logging.getLogger(config.LOG_BASE_NAME + '.' + __name__)


class NotImplementedYet(Exception):
    def __init__(self, message=None):
        Exception.__init__(self, message)


class UnknownStateError(Exception):
    def __init__(self, message=None):
        super().__init__(self, message)


class UserMistake(Exception):
    def __init__(self, message=None):
        Exception.__init__(self, message)

class InvalidSubmit(UserMistake): pass
class InvalidRequest(UserMistake): pass


class InvalidLanguage(UserMistake):
    TYPE = None
    def __init__(self, language=None):
        UserMistake.__init__(self, language)

class InvalidTargetLanguage(InvalidLanguage): TYPE = "target"
class InvalidSourceLanguage(InvalidLanguage): TYPE = "source"


def call_error(message, http_status_code, http_status_message=None):
    http_status = http_status_code if http_status_message == None else "{} {}".format(http_status_code, http_status_message)
    try:
        request_id = g.request_id
    except AttributeError:
        request_id = "unknown"

    return render_template("error_pages/general.html",
                           status_code=http_status_code,
                           status_message=http_status_message,
                           title=http_status,
                           message=message,
                           request_id=request_id
           ), http_status