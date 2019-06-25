import logging
import threading

import pyodbc as pyodbc
from flask import Flask, render_template, request, Blueprint, url_for, Response, stream_with_context
from flask_socketio import SocketIO, emit
from werkzeug.utils import redirect

import config
from shared.translation import Translation
from startup import http_server
from startup.http_server import socketio
from translate import translation
from translate.translation import add_translation_callback

blueprint = Blueprint('translate', __name__, url_prefix="/translate")
http_server.register_blueprint(blueprint)

LOG = logging.getLogger(config.LOG_BASE_NAME + '.' + __name__)

def stream_template(template_name, **context):
    # From http://flask.pocoo.org/docs/1.0/patterns/streaming/#streaming-from-templates
    # FIXME importing "main" seems like a really bad idea... This requires discussion on how to avoid this import and still be able to do this streaming
    import main
    main.app.update_template_context(context)
    t = main.app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(2)
    return rv

# @blueprint.route('/')
@blueprint.route('/text')
def index():
    user_translations = translation.user_translations_stream()
    LOG.info("opening translations page")
    return Response(
        stream_with_context(
            stream_template('translate/text.html', user_translations=user_translations)
        )
    )



@blueprint.route('/text', methods=['POST'])
def submit_translation():
    LOG.info("translation submission (POST), %s -> %s of: %s",
             request.form['sourceLanguage'], request.form['targetLanguage'], request.form['source_text'])
    translation.request_translation(request.form['source_text'],
                                    request.form['targetLanguage'],
                                    request.form['sourceLanguage'],
                                    user_id=request.sid)
    return redirect(request.full_path, code=303)

event_route = blueprint.url_prefix + "/text"

@socketio.on("connect")
def connect():
    print("connected")
    LOG.info("New client connected")


@socketio.on('translate this')
def translate_this(message):
    LOG.info("translation submission (POST), %s -> %s of: %s", message['sourceLanguage'], message['targetLanguage'], message['text'])
    translation_status = translation.request_translation(
        message['text'],
        message['targetLanguage'], message['sourceLanguage'],
        user_id=request.sid
    )
    announce_translation_update(translation_status)


def announce_translation_update(translation: Translation):
    LOG.info("Announcing a translation update: %s", translation)

    socketio.emit('translation update',
                  {
                      'uid': translation.uid,
                      'text': translation.text,
                      'translation': translation.translation,
                      'sourceLanguage': translation.source_language,
                      'targetLanguage': translation.target_language,
                      'status': translation.simplified_status,
                  },
                  include_self=True)

add_translation_callback(announce_translation_update)

@socketio.on('my event')
def test_message(message):
    sid = request.sid
    print("sid", sid)

    def late_reply(message, sid):
        pass
        socketio.emit('my response', {'data': 'got it!' + str(message)}, room=sid)  # requires SocketIO(... async_mode='threading') ?

    threading.Timer(2, late_reply, [message, sid]).start()
    socketio.emit('my response', {'data': 'have it!' + str(message)}, room=sid)
    emit('my response', {'data': 'Responding it!' + str(message)}, room=sid)
