import flask
from flask import g, session
from flask_babel import Babel

import config

available_translations = []

def babel(babel: Babel):
    global available_translations

    config.babel = babel

    available_translations = babel.list_translations()
    # from babel's source code of Locale.__init__, the str version has the location formatted with all parts, as expected
    available_translations = list(map(str, available_translations))

    @babel.localeselector
    def get_locale():
        return session['lang']

    @babel.timezoneselector
    def get_timezone():
        user = getattr(g, 'user', None)
        if user is not None:
            return user.timezone

