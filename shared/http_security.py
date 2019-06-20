import logging
import random
import sys
from functools import wraps

import numpy
from flask import g, session, request
from itsdangerous import URLSafeTimedSerializer

import config

LOG = logging.getLogger(config.LOG_BASE_NAME + '.' + __name__)

def form_token_protected(token_failure_callback=None):

    def protect_this(wrapped_f):
        def form_key():
            def key():
                return numpy.base_repr(random.randint(3330, sys.maxsize), 36)
            return key() + key() + key() + key()

        def new_token():
            g.current_form_token = form_key()
            LOG.debug("new token: %s", g.current_form_token)
            user_form_tokens = session.get('form_tokens', [])
            if len(user_form_tokens) > 20:
                del user_form_tokens[0:10]
            user_form_tokens.append(g.current_form_token)
            session['form_tokens'] = user_form_tokens

        @wraps(wrapped_f)
        def protection(*args, **kwargs):
            if request.method == "POST":
                g.form_token_filtered = False
                user_form_tokens = session.get('form_tokens', [])
                submitted_token = request.form.get(config.FORM_TOKEN_NAME, '')
                if submitted_token in user_form_tokens:
                    user_form_tokens.remove(submitted_token)
                    new_token()
                else:
                    LOG.info("Token failure: %s in %s. Submission: %s", submitted_token, user_form_tokens, request.form)
                    # If no token then the entity "was empty"
                    g.form_token_filtered = True
                    new_token()
                    if token_failure_callback != None:
                        return token_failure_callback()
                    request.form = dict()
            elif request.method == "GET":
                new_token()

            elif request.method == "VALIDATE":
                # To be used by javascript's XMLHTTPRequest or even a client's own development
                user_form_tokens = session.get('form_tokens', [])
                submitted_token = request.args.get(config.FORM_TOKEN_NAME, '')
                if submitted_token in user_form_tokens:
                    return "OK", "200 OK"
                return "INVALID TOKEN", "400 INVALID TOKEN"

            return wrapped_f(*args, **kwargs)
        return protection
    return protect_this


text_signer = URLSafeTimedSerializer(config.FLASK_LOGIN_SECRET_KEY)
