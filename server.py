import socket
import threading
import json
import time
import os
import hashlib

# ============================================================
#                    SERVER CONFIG
# ============================================================

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 9999        # Change if needed
MAX_CLIENTS = 50
BUFFER_SIZE = 8192

DATA_DIR = "server_data"
PLAYERS_DIR = os.path.join(DATA_DIR, "players")
LOGS_DIR = os.path.join(DATA_DIR, "logs")

# ============================================================
#                    SERVER STATE
# ============================================================

class ServerState:
    def __init__(self):
        self.clients = {}          # {addr: {"socket": sock, "name": name, "logged_in": bool}}
        self.online_players = {}   # {name: addr}
        self.chat_history = []     # Last 100 messages
        self.announcements = []
        self.lock = threading.Lock()
        self.running = True

        # Create directories
        os.makedirs(PLAYERS_DIR, exist_ok=True)
        os.makedirs(LOGS_DIR, exist_ok=True)

        self.log("Server initialized.")

    def log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}"
        print(log_line)
        try:
            log_file = os.path.join(LOGS_DIR, f"{time.strftime('%Y-%m-%d')}.log")
            with open(log_file, 'a') as f:
                f.write(log_line + "\n")
        except Exception:
            pass


server_state = ServerState()

# ============================================================
#                  PLAYER DATA MANAGEMENT
# ============================================================

def get_player_file(username):
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in username)
    return os.path.join(PLAYERS_DIR, f"{safe}.json")


def player_exists(username):
    return os.path.exists(get_player_file(username))


def create_player(username, password):
    """Create a new player account."""
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    data = {
        "username": username,
        "password_hash": pw_hash,
        "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        "last_login": time.strftime('%Y-%m-%d %H:%M:%S'),
        "game_state": {
            "money": 1000,
            "level": 1,
            "xp": 0,
            "xp_to_next": 100,
            "reputation": 0,
            "crypto_wallet": 0.0,
            "tools": ["nmap", "ping"],
            "files": ["readme.txt", "notes.txt"],
            "detection_level": 0,
            "vpn_active": False,
            "proxy_chains": 0,
            "botnet_size": 0,
            "known_passwords": {},
            "backdoors": [],
            "intercepted_data": [],
            "completed_missions": [],
            "compromised_targets": [],
            "notes": [],
            "tutorial_done": False,
        },
        "stats": {
            "total_logins": 1,
            "total_commands": 0,
            "targets_hacked": 0,
            "missions_completed": 0,
            "total_money_earned": 1000,
            "play_time_seconds": 0,
        },
    }
    try:
        with open(get_player_file(username), 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        server_state.log(f"Error creating player {username}: {e}")
        return False


def verify_player(username, password):
    """Verify player credentials."""
    if not player_exists(username):
        return False
    try:
        with open(get_player_file(username), 'r') as f:
            data = json.load(f)
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        return data["password_hash"] == pw_hash
    except Exception:
        return False


def load_player(username):
    """Load player data."""
    try:
        with open(get_player_file(username), 'r') as f:
            return json.load(f)
    except Exception:
        return None


def save_player(username, data):
    """Save player data."""
    try:
        with open(get_player_file(username), 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def update_player_state(username, game_state):
    """Update just the game state portion."""
    data = load_player(username)
    if data:
        data["game_state"] = game_state
        data["last_login"] = time.strftime('%Y-%m-%d %H:%M:%S')
        return save_player(username, data)
    return False


def update_player_stats(username, stats_update):
    """Update player stats."""
    data = load_player(username)
    if data:
        for key, value in stats_update.items():
            if key in data["stats"]:
                if isinstance(value, (int, float)):
                    data["stats"][key] += value
                else:
                    data["stats"][key] = value
        return save_player(username, data)
    return False


def get_leaderboard(sort_by="reputation", limit=20):
    """Get global leaderboard."""
    players = []
    try:
        for filename in os.listdir(PLAYERS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(PLAYERS_DIR, filename)
                with open(filepath, 'r') as f:
                    data = json.load(f)
                gs = data.get("game_state", {})
                players.append({
                    "name": data["username"],
                    "level": gs.get("level", 1),
                    "money": gs.get("money", 0),
                    "reputation": gs.get("reputation", 0),
                    "missions": len(gs.get("completed_missions", [])),
                    "online": data["username"] in server_state.online_players,
                })
    except Exception as e:
        server_state.log(f"Leaderboard error: {e}")

    players.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
    return players[:limit]


def get_online_players():
    """Get list of online players."""
    with server_state.lock:
        online = []
        for name, addr in server_state.online_players.items():
            data = load_player(name)
            if data:
                gs = data.get("game_state", {})
                online.append({
                    "name": name,
                    "level": gs.get("level", 1),
                })
        return online


# ============================================================
#                  REQUEST HANDLING
# ============================================================

def handle_request(request, client_addr):
    """Process a client request and return response."""
    try:
        action = request.get("action", "")
        response = {"status": "error", "message": "Unknown action"}

        # ── REGISTER ──
        if action == "register":
            username = request.get("username", "").strip()
            password = request.get("password", "").strip()
            if not username or not password:
                response = {"status": "error", "message": "Username and password required."}
            elif len(username) < 2 or len(username) > 20:
                response = {"status": "error", "message": "Username must be 2-20 characters."}
            elif len(password) < 4:
                response = {"status": "error", "message": "Password must be 4+ characters."}
            elif player_exists(username):
                response = {"status": "error", "message": "Username already taken."}
            else:
                if create_player(username, password):
                    server_state.log(f"New player registered: {username}")
                    response = {"status": "ok", "message": "Account created! You can now login."}
                else:
                    response = {"status": "error", "message": "Registration failed."}

        # ── LOGIN ──
        elif action == "login":
            username = request.get("username", "").strip()
            password = request.get("password", "").strip()
            if verify_player(username, password):
                with server_state.lock:
                    server_state.online_players[username] = client_addr
                data = load_player(username)
                if data:
                    data["last_login"] = time.strftime('%Y-%m-%d %H:%M:%S')
                    data["stats"]["total_logins"] += 1
                    save_player(username, data)

                server_state.log(f"Player logged in: {username}")
                # Broadcast to others
                broadcast_message(f"[SERVER] {username} has joined!", exclude=username)
                response = {
                    "status": "ok",
                    "message": f"Welcome back, {username}!",
                    "game_state": data["game_state"],
                    "stats": data["stats"],
                }
            else:
                response = {"status": "error", "message": "Invalid username or password."}

        # ── SAVE GAME ──
        elif action == "save":
            username = request.get("username", "")
            game_state = request.get("game_state", {})
            if username and username in server_state.online_players:
                if update_player_state(username, game_state):
                    response = {"status": "ok", "message": "Game saved."}
                else:
                    response = {"status": "error", "message": "Save failed."}
            else:
                response = {"status": "error", "message": "Not logged in."}

        # ── LEADERBOARD ──
        elif action == "leaderboard":
            sort_by = request.get("sort_by", "reputation")
            lb = get_leaderboard(sort_by)
            response = {"status": "ok", "leaderboard": lb}

        # ── WHO'S ONLINE ──
        elif action == "online":
            online = get_online_players()
            response = {"status": "ok", "players": online, "count": len(online)}

        # ── CHAT SEND ──
        elif action == "chat":
            username = request.get("username", "Unknown")
            message = request.get("message", "").strip()
            if not message:
                response = {"status": "error", "message": "Empty message."}
            elif len(message) > 200:
                response = {"status": "error", "message": "Message too long (200 max)."}
            else:
                timestamp = time.strftime('%H:%M:%S')
                chat_msg = {
                    "time": timestamp,
                    "user": username,
                    "text": message,
                }
                with server_state.lock:
                    server_state.chat_history.append(chat_msg)
                    if len(server_state.chat_history) > 100:
                        server_state.chat_history = server_state.chat_history[-100:]

                # Broadcast chat to all online players
                broadcast_chat(chat_msg, exclude=username)
                response = {"status": "ok", "message": "Message sent."}

        # ── GET CHAT HISTORY ──
        elif action == "chat_history":
            count = request.get("count", 20)
            with server_state.lock:
                history = server_state.chat_history[-count:]
            response = {"status": "ok", "messages": history}

        # ── PLAYER PROFILE ──
        elif action == "profile":
            target = request.get("target", "")
            data = load_player(target)
            if data:
                gs = data.get("game_state", {})
                response = {
                    "status": "ok",
                    "profile": {
                        "name": data["username"],
                        "level": gs.get("level", 1),
                        "money": gs.get("money", 0),
                        "reputation": gs.get("reputation", 0),
                        "missions": len(gs.get("completed_missions", [])),
                        "tools": len(gs.get("tools", [])),
                        "online": data["username"] in server_state.online_players,
                        "last_login": data.get("last_login", "unknown"),
                        "created": data.get("created", "unknown"),
                        "total_logins": data.get("stats", {}).get("total_logins", 0),
                    }
                }
            else:
                response = {"status": "error", "message": "Player not found."}

        # ── LOGOUT ──
        elif action == "logout":
            username = request.get("username", "")
            game_state = request.get("game_state", {})
            if username:
                if game_state:
                    update_player_state(username, game_state)
                with server_state.lock:
                    if username in server_state.online_players:
                        del server_state.online_players[username]
                server_state.log(f"Player logged out: {username}")
                broadcast_message(f"[SERVER] {username} has left.", exclude=username)
                response = {"status": "ok", "message": "Logged out. Game saved."}

        # ── PING ──
        elif action == "ping":
            response = {"status": "ok", "message": "pong", "time": time.time()}

        # ── SERVER INFO ──
        elif action == "info":
            total_players = len(os.listdir(PLAYERS_DIR)) if os.path.exists(PLAYERS_DIR) else 0
            online_count = len(server_state.online_players)
            response = {
                "status": "ok",
                "server": "HackStorm Server v2.0",
                "total_players": total_players,
                "online": online_count,
                "uptime": "running",
            }

        return response

    except Exception as e:
        server_state.log(f"Request error: {e}")
        return {"status": "error", "message": "Server error."}


def broadcast_message(message, exclude=None):
    """Send a message to all connected clients."""
    notification = {
        "type": "notification",
        "message": message,
        "time": time.strftime('%H:%M:%S'),
    }
    broadcast_to_all(notification, exclude)


def broadcast_chat(chat_msg, exclude=None):
    """Send a chat message to all connected clients."""
    notification = {
        "type": "chat",
        "data": chat_msg,
    }
    broadcast_to_all(notification, exclude)


def broadcast_to_all(data, exclude=None):
    """Send data to all connected clients."""
    encoded = (json.dumps(data) + "\n").encode('utf-8')
    with server_state.lock:
        for name, addr in list(server_state.online_players.items()):
            if name == exclude:
                continue
            for caddr, cinfo in server_state.clients.items():
                if cinfo.get("name") == name:
                    try:
                        cinfo["socket"].sendall(encoded)
                    except Exception:
                        pass


# ============================================================
#                  CLIENT HANDLER
# ============================================================

def handle_client(client_socket, client_addr):
    """Handle a connected client."""
    server_state.log(f"New connection: {client_addr}")
    client_name = None

    with server_state.lock:
        server_state.clients[client_addr] = {
            "socket": client_socket,
            "name": None,
            "logged_in": False,
        }

    buffer = ""

    try:
        while server_state.running:
            try:
                data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break

                buffer += data

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        request = json.loads(line)
                    except json.JSONDecodeError:
                        response = {"status": "error", "message": "Invalid JSON."}
                        client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))
                        continue

                    # Track username
                    if request.get("action") == "login" and not client_name:
                        pass  # Will be set after successful login
                    if request.get("action") == "register":
                        pass

                    response = handle_request(request, client_addr)

                    # Track login
                    if request.get("action") == "login" and response.get("status") == "ok":
                        client_name = request.get("username")
                        with server_state.lock:
                            server_state.clients[client_addr]["name"] = client_name
                            server_state.clients[client_addr]["logged_in"] = True

                    client_socket.sendall((json.dumps(response) + "\n").encode('utf-8'))

            except ConnectionResetError:
                break
            except Exception as e:
                server_state.log(f"Client error {client_addr}: {e}")
                break

    finally:
        # Cleanup on disconnect
        if client_name:
            with server_state.lock:
                if client_name in server_state.online_players:
                    del server_state.online_players[client_name]
            broadcast_message(f"[SERVER] {client_name} has disconnected.")
            server_state.log(f"Player disconnected: {client_name}")

        with server_state.lock:
            if client_addr in server_state.clients:
                del server_state.clients[client_addr]

        try:
            client_socket.close()
        except Exception:
            pass

        server_state.log(f"Connection closed: {client_addr}")


# ============================================================
#                    SERVER MAIN
# ============================================================

def server_console():
    """Server admin console."""
    while server_state.running:
        try:
            cmd = input()
            parts = cmd.strip().split()
            if not parts:
                continue
            command = parts[0].lower()

            if command == "help":
                print("Commands: help, online, players, kick <name>, announce <msg>, stats, stop")
            elif command == "online":
                online = get_online_players()
                print(f"Online ({len(online)}):")
                for p in online:
                    print(f"  {p['name']} (Lvl {p['level']})")
            elif command == "players":
                files = os.listdir(PLAYERS_DIR) if os.path.exists(PLAYERS_DIR) else []
                print(f"Total registered: {len(files)}")
                for f in files:
                    print(f"  {f.replace('.json', '')}")
            elif command == "kick" and len(parts) > 1:
                name = parts[1]
                with server_state.lock:
                    if name in server_state.online_players:
                        del server_state.online_players[name]
                        print(f"Kicked {name}")
                        broadcast_message(f"[SERVER] {name} was kicked.")
                    else:
                        print(f"{name} not online.")
            elif command == "announce" and len(parts) > 1:
                msg = " ".join(parts[1:])
                broadcast_message(f"[ANNOUNCEMENT] {msg}")
                print(f"Announced: {msg}")
            elif command == "stats":
                online = len(server_state.online_players)
                total = len(os.listdir(PLAYERS_DIR)) if os.path.exists(PLAYERS_DIR) else 0
                print(f"Online: {online} | Total Players: {total}")
            elif command == "stop":
                print("Shutting down...")
                server_state.running = False
                broadcast_message("[SERVER] Server shutting down!")
                break
            else:
                print(f"Unknown: {command}. Type 'help'.")
        except EOFError:
            break
        except Exception as e:
            print(f"Console error: {e}")


def main():
    print("=" * 50)
    print("  HackStorm Server v2.0")
    print(f"  Listening on {HOST}:{PORT}")
    print("  Type 'help' for server commands")
    print("=" * 50)
    print()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.settimeout(1.0)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(MAX_CLIENTS)
        server_state.log(f"Server started on {HOST}:{PORT}")

        # Start admin console
        console_thread = threading.Thread(target=server_console, daemon=True)
        console_thread.start()

        while server_state.running:
            try:
                client_socket, client_addr = server_socket.accept()
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_addr),
                    daemon=True
                )
                client_thread.start()
            except socket.timeout:
                continue
            except Exception as e:
                if server_state.running:
                    server_state.log(f"Accept error: {e}")

    except Exception as e:
        server_state.log(f"Fatal error: {e}")
    finally:
        server_socket.close()
        server_state.log("Server stopped.")


if __name__ == "__main__":
    main()