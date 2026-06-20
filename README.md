# AnonChat 🧅
 
A real-time anonymous chat room running as a Tor hidden service (.onion site).
No accounts. No logs. No IP addresses. Just chat.
 
---
 
## What it is
 
AnonChat is a lightweight anonymous chat room that runs entirely over the Tor network.
Visitors connect through Tor Browser, get assigned a random identity (Anon1, Anon2, etc.),
and can chat in real time with anyone else on the site. When the server restarts, all
messages are gone — no history, no trace.
 
---
 
## Tech stack
 
| Layer | Technology |
|---|---|
| Web framework | Python Flask |
| Real-time messaging | Flask-SocketIO (polling transport) |
| Anonymity network | Tor hidden service (.onion) |
| Process manager | systemd |
| Server | Ubuntu/Debian VPS |
 
---
 
## Project structure
 
```
/opt/anonchat/
├── app.py              # Flask server + WebSocket logic
└── templates/
    └── index.html      # Chat UI (dark theme, single file)
```
 
---
 
## How it works
 
```
Visitor's Tor Browser
      ↓ (encrypted through Tor network)
Tor hidden service (.onion address)
      ↓ (local)
Flask-SocketIO server on 127.0.0.1:8081
      ↓ (broadcast)
All connected users see the message instantly
```
 
- Each visitor gets assigned `Anon{N}` where N is a global counter that never resets
- Messages are broadcast to all connected users via Socket.IO polling
- No database — messages live in RAM only
- Disconnecting permanently removes your session
---
 
## Setup on a fresh Ubuntu/Debian VPS
 
### 1. Install dependencies
 
```bash
apt update && apt upgrade -y
apt install -y python3 python3-pip tor
pip3 install flask flask-socketio --break-system-packages
```
 
### 2. Create project folder
 
```bash
mkdir -p /opt/anonchat/templates
```
 
### 3. Upload your files
 
From your local Windows machine:
 
```powershell
scp app.py root@YOUR_SERVER_IP:/opt/anonchat/app.py
scp templates/index.html root@YOUR_SERVER_IP:/opt/anonchat/templates/index.html
```
 
### 4. Configure Tor hidden service
 
Edit `/etc/tor/torrc` and add at the bottom:
 
```
HiddenServiceDir /var/lib/tor/anonchat/
HiddenServicePort 80 127.0.0.1:8081
```
 
Restart Tor:
 
```bash
systemctl restart tor
```
 
Get your .onion address:
 
```bash
cat /var/lib/tor/anonchat/hostname
```
 
### 5. Fix index.html Socket.IO transport
 
```bash
sed -i "s/const socket = io();/const socket = io({ transports: ['polling'] });/" /opt/anonchat/templates/index.html
```
 
### 6. Create systemd service
 
```bash
cat > /etc/systemd/system/anonchat.service << 'SEOF'
[Unit]
Description=AnonChat Flask App
After=network.target
 
[Service]
WorkingDirectory=/opt/anonchat
ExecStart=/usr/bin/python3 /opt/anonchat/app.py
Restart=always
RestartSec=5
 
[Install]
WantedBy=multi-user.target
SEOF
```
 
Enable and start:
 
```bash
systemctl daemon-reload
systemctl enable anonchat
systemctl start anonchat
systemctl status anonchat
```
 
---
 
## app.py
 
```python
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
counter = 0
 
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
    socketio.run(app, host='127.0.0.1', port=8081, debug=False, allow_unsafe_werkzeug=True)
```
 
---
 
## Useful commands
 
```bash
# Check if app is running
systemctl status anonchat
 
# View live logs
journalctl -u anonchat -f
 
# Restart the app
systemctl restart anonchat
 
# Check what port the app is on
ss -tlnp | grep 8081
 
# Get your .onion address
cat /var/lib/tor/anonchat/hostname
 
# Check Tor is running
systemctl status tor
```
 
---
 
## Important notes
 
- **HTTP is fine** — .onion sites do not need HTTPS. Tor provides end-to-end encryption natively.
- **Messages are not stored** — when the server restarts, all chat history is gone.
- **Port conflict** — if something else uses port 8081, change it in both `app.py` and `torrc`.
- **Private key** — your .onion address is stored in `/var/lib/tor/anonchat/`. Back it up if you want to keep the same address.
---
 
## Backup your .onion identity
 
```bash
# Back up your .onion private key (keep this safe!)
cat /var/lib/tor/anonchat/hs_ed25519_secret_key | base64
```
 
If you lose this file, your .onion address is gone forever.
 
---
 
## Ideas for next steps
 
- Add message encryption (PyCryptodome) so messages are encrypted at rest
- Add rooms / channels
- Add file upload support (Project 7 — SecureDrop clone)
- Add rate limiting to prevent spam
- Generate a vanity .onion address with mkp224o
---
 
*Built with Flask + Tor. Runs on the dark web. 🧅*
 
