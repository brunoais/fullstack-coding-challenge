import logging
import random
import sys

import flask
import itertools
import numpy
import requests
from werkzeug.urls import url_decode
from flask import Flask, g, redirect, request, url_for
from flask_babel import gettext
from babel import negotiate_locale

import config
import shared.exceptions
import shared.formatters
import startup.top_menu
from shared.exceptions import call_error
from shared.flask import request_type
from shared.global_enums import UserMessageTypes
from startup.top_menu import SpecialPageEntry

LOG = logging.getLogger(config.LOG_BASE_NAME + '.' + __name__)

socketio: 'flask_socketio.SocketIO' = None

class HTTPMethodOverrideFilter(object):
    allowed_methods = frozenset([
        'AUTOFILL',
        'DELETE',
        'GET',
        'HEAD',
        'LOGIN',
        'OPTIONS',
        'PATCH',
        'POST',
        'PUT',
        'RECLASS',
    ])
    bodyless_methods = frozenset(['GET', 'HEAD', 'OPTIONS', 'DELETE'])

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()
        if not method and '_real_method=' in environ.get('QUERY_STRING', ''):
            method = url_decode(environ['QUERY_STRING']).get('_real_method')
        if method in self.allowed_methods:
            method = method.encode('ascii', 'replace')
            environ['REQUEST_METHOD'] = method
        if method in self.bodyless_methods:
            environ['CONTENT_LENGTH'] = '0'
        return self.app(environ, start_response)


def setup_server(app: Flask, sanity_check=True):
    """
    :param sanity_check: Used by unit tests so the sanity check isn't run
    """
    app.wsgi_app = HTTPMethodOverrideFilter(app.wsgi_app)
    app.config['SECRET_KEY'] = 'shhhhhh seeeecret'
    app.config['LOGGER_HANDLER_POLICY'] = 'always'

    if sanity_check:
        @app.before_first_request
        def sanity_check():
            fail_messages = []
            def ensure(test, message):
                if not test:
                    fail_messages.append(message)

            if fail_messages:
                LOG.fatal("Flask cannot start due to missing prerequisites: \n - %s", "\n - ".join(fail_messages))
                exit(17)


    @app.before_request
    def g_request_type():
        g.request_type = request_type()

    @app.before_request
    def request_id():
        # 13330 = AAA in base 36
        key1 = random.randint(13330, sys.maxsize)
        key2 = random.randint(13330, sys.maxsize)
        # Use the whole alphanumeric
        request_id = numpy.base_repr(key1, 36) + numpy.base_repr(key2, 36)
        LOG.info('Starting request: %s', request_id)
        g.request_id = request_id


    @app.after_request
    def request_id_in_response(response):
        response.headers['X-Request-ID'] = g.request_id

        return response


def setup_global_error_handlers(app: Flask):

    @app.errorhandler(shared.exceptions.InvalidLanguage)
    def invalid_submit_data(e):
        LOG.warning('User sent a language that is invalid', e, exc_info=e)
        return shared.exceptions.call_error("The {type} language is not allowed".format(type=e.TYPE), 422, "REFUSED INPUT")


    @app.errorhandler(shared.exceptions.InvalidSubmit)
    def invalid_submit_data(e):
        LOG.warning('browser sent wrong data in POST', e, exc_info=e)
        return shared.exceptions.call_error("The form did not submit correctly.", 422, "BAD ACCESS")

    @app.errorhandler(shared.exceptions.InvalidRequest)
    def invalid_request(e):
        LOG.warning('browser sent wrong data for processing', exc_info=e)
        return shared.exceptions.call_error("Couldn't process request due to missing data", 400)

    # There is no easy-to-find way of knowing how can a blueprint register a handler for functions that belong to its file instead of only for its blueprint
    # By default, a blueprint's error handler can only handle errors related to its own blueprint.

    @app.errorhandler(requests.exceptions.HTTPError)
    def requests_unusual_status(e):
        status_code = e.response.status_code
        status_text = e.response.reason

        if status_code == 404:
            LOG.exception("Backend responded that resource doesn't exist: %s", e.request)
            return call_error("The backend server did not respond properly", 503)
        if status_code == 409:
            LOG.exception('Backend rejected, the input that was given: %s', e.request)
            return call_error("The information you submit was invalid for an unspecified reason. Try something else.", 409)
        if status_code == 500:
            LOG.exception('Cannot service response due to a fault in a dependent service')
            return call_error("The backend server failed to respond as expected", 503)
        if status_code == 502:
            LOG.exception('Backend server responded as Bad Gateway')
            return call_error("The backend server failed to respond try again in a few minutes", 503)

        return general_exception(e)

    @app.errorhandler(Exception)
    def general_exception(e):
        LOG.exception('Unexpected exception')
        return call_error("Unexpected exception happened. No details available", 500)

    @app.errorhandler(400)
    def server_error(e):
        LOG.exception('An invalid request was made')
        return call_error(e.description, 400)

    @app.errorhandler(404)
    def server_error(e):
        LOG.exception('Requested something that doesn\'t exist')
        return call_error(e.description, 404)

    @app.errorhandler(405)
    def server_error(e):
        LOG.exception('Wrong method was used')
        return call_error("Method Not Allowed", 405)

    @app.errorhandler(500)
    def server_error(e):
        LOG.exception('An error occurred during a request.')
        return call_error(e.description, 500)


def setup_app_jinja(app: Flask):
    app.jinja_env.trim_blocks = True  # Delete newlines after tags (removes excessive newlines in the output)
    app.jinja_env.lstrip_blocks = True  # Delete whitespace at the left of the control tags (easier to read HTML)
    app.jinja_env.add_extension('jinja2.ext.do')


    @app.context_processor
    def eq_enum():
        def eq_enum(left, right): return left is right
        return dict(eq_enum=eq_enum)

    @app.context_processor
    def top_menu():
        return dict(top_menu=startup.top_menu.top_menu)

    @app.context_processor
    def static_url_for():
        from shared.formatters import statics_url_for
        return dict(static_url_for=statics_url_for)


def setup_global_routes(app: Flask):
    @app.route('/')
    @app.route('/index')
    def index():
        return redirect(url_for('translate.index'), code=303)

def setup_events_comms(app: Flask):
    global socketio
    from flask_socketio import SocketIO

    socketio = SocketIO(app, engineio_logger=True, async_mode='threading')
    # socketio = SocketIO(app, engineio_logger=True, async_mode='gevent')
    # socketio = SocketIO(app, engineio_logger=True)



pending_blueprints = []


# call register_blueprint_module instead
def _register_blueprint_module_queue(blueprint):
    pending_blueprints.append(blueprint)


def register_app_blueprints(app: Flask):
    global _register_blueprint

    # Doing like this allows retaining the function name which can be used to know which function will be run; for debugging purposes
    def _register_blueprint_now(blueprint):
        app.register_blueprint(blueprint)
    _register_blueprint = _register_blueprint_now

    for blueprint in pending_blueprints:
        register_blueprint(blueprint)


# value changes when register_blueprints() is called
_register_blueprint = _register_blueprint_module_queue


# using a function prevents misuse by code that would import the variable directly instead of the module
def register_blueprint(blueprint):
    _register_blueprint(blueprint)



special_pages = []


def specialPageEntry(section_key, section_permission, redirect_order):
    special_pages.append(SpecialPageEntry(section_key, section_permission, redirect_order))



def run_local_dev(app: Flask):
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.run(host='0.0.0.0', port=5000, debug=True)

