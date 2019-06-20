import logging
from functools import wraps

from flask import request

import config
from shared.global_enums import RequestType

LOG = logging.getLogger(config.LOG_BASE_NAME + '.' + __name__)

def maintain_g_global(f):
    from flask import g, current_app
    # http://flask.pocoo.org/docs/1.0/reqcontext/#notes-on-proxies
    outside_app = current_app._get_current_object()
    outside_g = g._get_current_object()

    @wraps(f)
    def wrapped(*args, **kwargs):
        with outside_app.app_context():
            try:
                g._get_current_object().__dict__.update(outside_g.__dict__)
            except:
                LOG.exception("Failed to copy external state to current state for call")
            return f(*args, **kwargs)
    return wrapped


def request_type(environ=None):
    if (environ or request.environ)['PATH_INFO'].startswith('/static/'):
        return RequestType.STATIC
    return RequestType.NORMAL


def request_id_in_logs():
    old_factory = logging.getLogRecordFactory()
    try:
        from flask import has_app_context, g
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            if has_app_context():
                try:
                    record.request_id = g.request_id
                except AttributeError:
                    record.request_id = "NO_REQUEST_ID"
            else:
                record.request_id = "NON_REQUEST"
            return record
        logging.setLogRecordFactory(record_factory)
    except ImportError:
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.request_id = "NO_FLASK"
            return record
        logging.setLogRecordFactory(record_factory)
        print("Cannot setup logging_id for Flask")

        LOG.exception("Cannot setup logging_id for Flask")
