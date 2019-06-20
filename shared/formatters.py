import logging
import uuid

import config


LOG = logging.getLogger(config.LOG_BASE_NAME + '.' + __name__)


def date_format(date, format='medium'):
    import dateutil
    import flask_babel
    LOG.debug("formatting date %s", date)
    try:
        if isinstance(date, str):
            date = dateutil.parser.isoparse(date)
        return flask_babel.format_date(date, format)
    except ValueError:
        LOG.exception("Value '%s' is not in a valid ISO format (or is too obscure format)", date)
    return date


def datetime_format(date, format='medium'):
    import dateutil
    import flask_babel
    LOG.debug("formatting datetime %s", date)
    try:
        if isinstance(date, str):
            date = dateutil.parser.isoparse(date)
        return flask_babel.format_datetime(date, format)
    except ValueError:
        LOG.exception("Value '%s' is not in a valid ISO format (or is too obscure format)", date)
    return date


def statics_url_for():
    import os
    from flask import url_for
    version = os.environ.get('GAE_VERSION', str(uuid.uuid4())[0:15])
    def statics_url_for(file, **values):
        values['v'] = version
        return url_for('static', filename=file, **values)
    return statics_url_for
try:
    statics_url_for = statics_url_for()
except ModuleNotFoundError:
    LOG.exception("Cannot find flask's url_for")
