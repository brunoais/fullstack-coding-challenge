import threading

import pyodbc as pyodbc
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# socketio = SocketIO(app, engineio_logger=True, async_mode='threading')
socketio = SocketIO(app, engineio_logger=True, async_mode='gevent')
# socketio = SocketIO(app, engineio_logger=True)


@app.route('/')
def index():
    return render_template('sockets.html')

@socketio.on("connect")
def connect():
    print("connected")

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

conn_str = (
    "DRIVER={PostgreSQL Unicode};"
    "DATABASE=postgres;"
    "UID=user;"
    "PWD=testingpassword;"
    "SERVER=localhost;"
    "PORT=5432;"
)

cnxn = pyodbc.connect(conn_str)

cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
cnxn.setencoding(encoding='utf-8')
cnxn.maxwrite = 1024 * 1024 * 1024
#
# tables_query = cnxn.execute("INSERT INTO  * from information_schema.tables ")
#
# row = tables_query.fetchone()
# print(repr(row))

if __name__ == '__main__':
    socketio.run(app, port=5000)
