from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zync-chat-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# In-memory store: {room: {sid: username}}
rooms = {}


# ── Database ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                room     TEXT    NOT NULL DEFAULT 'general',
                username TEXT    NOT NULL,
                message  TEXT    NOT NULL,
                time     TEXT    NOT NULL
            )
        ''')
        conn.commit()

init_db()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# ── Socket events ─────────────────────────────────────────────────────────────

@socketio.on('connect')
def on_connect():
    emit('room_list', _room_names())

@socketio.on('get_rooms')
def on_get_rooms():
    emit('room_list', _room_names())

@socketio.on('join')
def on_join(data):
    username = data.get('username', '').strip()
    room     = data.get('room', 'general').strip() or 'general'
    sid      = request.sid

    # Leave any current room
    for r, members in list(rooms.items()):
        if sid in members:
            del members[sid]
            leave_room(r)
            emit('user_list', _user_list(r), room=r)

    # Join new room
    join_room(room)
    if room not in rooms:
        rooms[room] = {}
    rooms[room][sid] = username

    emit('room_list', _room_names(), broadcast=True)
    emit('user_list', _user_list(room), room=room)

    # Send message history for this room
    with get_db() as conn:
        rows = conn.execute(
            'SELECT username, message, time FROM messages WHERE room=? ORDER BY id ASC LIMIT 100',
            (room,)
        ).fetchall()
    emit('load_messages', [dict(r) for r in rows])

@socketio.on('message')
def on_message(data):
    username = data.get('username', 'anon')
    message  = data.get('message', '').strip()
    room     = data.get('room', 'general')
    if not message:
        return

    time_str = datetime.now().strftime('%H:%M')

    with get_db() as conn:
        conn.execute(
            'INSERT INTO messages (room, username, message, time) VALUES (?,?,?,?)',
            (room, username, message, time_str)
        )
        conn.commit()

    emit('message', {
        'username': username,
        'message':  message,
        'time':     time_str,
        'room':     room,
    }, room=room)

@socketio.on('typing')
def on_typing(data):
    emit('typing', data, room=data.get('room', 'general'), include_self=False)

@socketio.on('seen')
def on_seen(data):
    emit('seen', data, room=data.get('room', 'general'), include_self=False)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    for r, members in list(rooms.items()):
        if sid in members:
            del members[sid]
            emit('user_list', _user_list(r), room=r)
            if not members:
                del rooms[r]
            emit('room_list', _room_names(), broadcast=True)
            break


# ── Helpers ───────────────────────────────────────────────────────────────────

def _room_names():
    names = list(rooms.keys())
    if 'general' not in names:
        names.insert(0, 'general')
    return names

def _user_list(room):
    return list(rooms.get(room, {}).values())


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
