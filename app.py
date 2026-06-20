from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tor-chat-secret'
socketio = SocketIO(
    app,
    async_mode='threading',
    cors_allowed_origins='*',
    transports=['polling']
)

users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    global counter
    counter += 1
    name = f"Anon{counter}"
    users[request.sid] = name
    emit('system_message', {'message': f"Welcome! You are {name}"})
    emit('system_message', {'message': f"{name} joined the chat"}, broadcast=True)
    emit('user_count', {'count': len(users)}, broadcast=True)

@socketio.on('disconnect')
def on_disconnect():
    name = users.pop(request.sid, 'Someone')
    emit('system_message', {'message': f"{name} left the chat"}, broadcast=True)
    emit('user_count', {'count': len(users)}, broadcast=True)

@socketio.on('message')
def on_message(data):
    name = users.get(request.sid, 'Anon')
    if isinstance(data, dict):
        msg = data.get('message') or data.get('msg') or str(data)
    else:
        msg = str(data)
    emit('chat_message', {'sender': name, 'message': msg}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8080, debug=False, allow_unsafe_werkzeug=True)