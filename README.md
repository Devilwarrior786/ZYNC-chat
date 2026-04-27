# ZYNC-chat

**✨ Features**
**Messaging**

Real-time messaging with zero page reloads via WebSockets (Socket.IO)
Message history loaded on room join (last 100 messages persisted in SQLite)
Live typing indicator — shows who's currently typing
Message timestamps on every bubble

**Rooms**

Multi-room support — join or create any room instantly
Room list in sidebar updates live as rooms are created
Seamless room switching without losing your session
Graceful room cleanup when last user leaves

**Users**

Live online users panel showing everyone in the current room
Colour-coded avatars (initials-based) for each participant
Real-time join/leave updates — user list stays in sync automatically
Green presence dot for all active members

**UI / UX**

Clean, modern editorial design with warm ink-on-paper aesthetic
Responsive sidebar with room list and user panel
Auto-expanding message input (Shift+Enter for new lines, Enter to send)
Smooth animations on messages, modals, and transitions
Custom scrollbar and lined-paper background texture

**Backend**

Flask + Flask-SocketIO backend with Eventlet async support
SQLite database with per-room message storage
CORS enabled for flexible deployment
Graceful disconnect handling — cleans up users and empty rooms automatically

**Important Note**
the current version is runinng in localhost,to share with everyone and chat you need to give your ip adrress
this path you need to place ip address.

**Stack**

Backend: Python, Flask, Flask-SocketIO, SQLite
Frontend: Vanilla HTML/CSS/JS, Socket.IO client
Fonts: Instrument Serif, Instrument Sans, JetBrains Mono
