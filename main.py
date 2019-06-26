import pkgutil
import importlib

# load all startup packages
# from flask_babel import Babel

for _, package_name, _ in pkgutil.iter_modules(["startup"], prefix='startup.'):
    importlib.import_module(package_name)

import startup.http_server

import config
from shared import boot_queue

from startup.http_server import flask

app = flask.Flask(__name__)
# babel = Babel(app)


startup.http_server.setup_server(app)
startup.http_server.setup_global_error_handlers(app)
startup.http_server.setup_app_jinja(app)
startup.http_server.setup_global_routes(app)

if __name__ == '__main__':
    startup.http_server.setup_events_comms(app, 'threading')
else:
    startup.http_server.setup_events_comms(app)

from translate import http

startup.http_server.register_app_blueprints(app)

boot_queue.boot_queue.run_startup_tasks()


if __name__ == '__main__':
    startup.http_server.run_local_dev(app)

