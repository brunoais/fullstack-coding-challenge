import os
from collections import namedtuple

os.environ['UNBABEL_API_KEY'] = 'does not matter for unit tests'

import config
config.UNIT_TESTS = True


import pytest

@pytest.fixture(scope="module")
def pages_app():
    from startup import http_server
    from flask import Flask
    app = Flask(__name__, template_folder="../templates")
    http_server.setup_app_jinja(app)
    app.testing = True
    app.config['SECRET_KEY'] = "tests_key"
    return app

@pytest.fixture(scope="module")
def app():
    from flask import Flask
    app = Flask(__name__)
    app.testing = True
    yield app

@pytest.fixture(scope="function")
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture(scope="function")
def pages_app(app, client):
    import startup.http_server
    startup.http_server.setup_server(app, sanity_check=False)
    yield client


@pytest.fixture(scope="function")
def blueprinted_server(app, pages_app, request):
    from startup import http_server

    pending_blueprints = http_server.pending_blueprints + getattr(request, 'args', [])

    for blueprint in pending_blueprints:
        app.register_blueprint(blueprint)

    yield pages_app


RequestContext = namedtuple('RequestContext', ['context', 'client'])

@pytest.fixture(scope="function")
def app_context(app, pages_app):
    with app.app_context() as ctx:
        yield RequestContext(ctx, pages_app)



class BlackHoleObject(object):
    def __getattr__(self, item):
        return self.__dict__.get(item, self)
    def __setattr__(self, item, value):
        self.__dict__[item] = value
    def __call__(self, *args, **kwargs):
        return self
    def __bool__(self):
        return False

