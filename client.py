import socket
import json
import threading
import sys
import time
import os
import getpass

# ============================================================
#                    CLIENT CONFIG
# ============================================================

# CHANGE THIS to your server's IP address!
SERVER_HOST = "192.168.0.57"  # localhost for testing, change to your server IP
SERVER_PORT = 9999
BUFFER_SIZE = 8192

# ============================================================
#                    COLORS
# ============================================================

def enable_ansi():
    if os.name == 'nt':
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7
            )
            return True
        except Exception:
            pass
        if any(os.environ.get(v) for v in ['WT_SESSION', 'TERM_PROGRAM']):
            return True
        try:
            os.system('')
            return True
        except Exception:
            return False
    return True

USE_COLORS = enable_ansi()

class C:
    if USE_COLORS:
        RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
        BLUE = "\033[94m"; MAGENTA = "\033[95m"; CYAN = "\033[96m"
        WHITE = "\033[97m"; ORANGE = "\033[38;5;208m"
        GOLD = "\033[38;5;220m"; PINK = "\033[38;5;205m"
        LIME = "\033[38;5;118m"; PURPLE = "\033[38;5;129m"
        STEEL = "\033[38;5;244m"; NEON_GREEN = "\033[38;5;46m"
        BOLD = "\033[1m"; DIM = "\033[2m"; RESET = "\033[0m"
        BG_RED = "\033[41m"; BG_GREEN = "\033[42m"
        BG_DARK = "\033[48;5;235m"
    else:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
        ORANGE = GOLD = PINK = LIME = PURPLE = STEEL = NEON_GREEN = ""
        BOLD = DIM = RESET = BG_RED = BG_GREEN = BG_DARK = ""


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def p(text, color=""):
    if USE_COLORS and color:
        print(color + text + C.RESET)
    else:
        print(text)


# ============================================================
#                NETWORK CLIENT
# ============================================================

class GameClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.username = None
        self.game_state = None
        self.listener_thread = None
        self.pending_notifications = []
        self.lock = threading.Lock()

    def connect(self, host, port):
        """Connect to server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((host, port))
            self.connected = True

            # Start listener thread
            self.listener_thread = threading.Thread(target=self._listener, daemon=True)
            self.listener_thread.start()

            return True
        except Exception as e:
            p(f"  [ERROR] Cannot connect to {host}:{port}", C.RED)
            p(f"  {e}", C.DIM)
            return False

    def disconnect(self):
        """Disconnect from server."""
        if self.connected and self.username:
            try:
                self.send_request({
                    "action": "logout",
                    "username": self.username,
                    "game_state": self.game_state or {},
                })
            except Exception:
                pass
        self.connected = False
        try:
            self.socket.close()
        except Exception:
            pass

    def send_request(self, request):
        """Send request and get response."""
        if not self.connected:
            return {"status": "error", "message": "Not connected."}
        try:
            data = json.dumps(request) + "\n"
            self.socket.sendall(data.encode('utf-8'))

            # Wait for response (with timeout)
            start = time.time()
            while time.time() - start < 10:
                with self.lock:
                    # Check if we got a response (non-notification)
                    pass
                time.sleep(0.05)

            # Read response directly
            return self._read_response()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _read_response(self):
        """Read a response from the server."""
        try:
            self.socket.settimeout(10)
            buffer = ""
            while True:
                data = self.socket.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    return {"status": "error", "message": "Disconnected."}
                buffer += data
                if "\n" in buffer:
                    line, _ = buffer.split("\n", 1)
                    return json.loads(line)
        except socket.timeout:
            return {"status": "error", "message": "Timeout."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _listener(self):
        """Background thread to listen for server notifications."""
        buffer = ""
        while self.connected:
            try:
                self.socket.settimeout(1)
                data = self.socket.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    try:
                        msg = json.loads(line)
                        if msg.get("type") == "notification":
                            with self.lock:
                                self.pending_notifications.append(msg)
                        elif msg.get("type") == "chat":
                            with self.lock:
                                self.pending_notifications.append(msg)
                    except json.JSONDecodeError:
                        pass
            except socket.timeout:
                continue
            except Exception:
                break

    def get_notifications(self):
        """Get and clear pending notifications."""
        with self.lock:
            notifs = self.pending_notifications.copy()
            self.pending_notifications.clear()
        return notifs

    def simple_request(self, request):
        """Simple send and receive."""
        if not self.connected:
            return {"status": "error", "message": "Not connected."}
        try:
            data = json.dumps(request) + "\n"
            self.socket.sendall(data.encode('utf-8'))

            self.socket.settimeout(10)
            buffer = ""
            while True:
                chunk = self.socket.recv(BUFFER_SIZE).decode('utf-8')
                if not chunk:
                    return {"status": "error", "message": "Disconnected."}
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    try:
                        parsed = json.loads(line)
                        # If it's a notification, queue it and keep waiting
                        if parsed.get("type") in ("notification", "chat"):
                            with self.lock:
                                self.pending_notifications.append(parsed)
                            continue
                        return parsed
                    except json.JSONDecodeError:
                        continue
        except socket.timeout:
            return {"status": "error", "message": "Timeout."}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# ============================================================
#                    ONLINE GAME CLIENT
# ============================================================

class HackStormOnline:
    def __init__(self):
        self.client = GameClient()
        self.running = True
        self.auto_save_counter = 0

    def show_banner(self):
        clear()
        print()
        p("  ╦ ╦╔═╗╔═╗╦╔═╔═╗╔╦╗╔═╗╦═╗╔╦╗", C.CYAN)
        p("  ╠═╣╠═╣║  ╠╩╗╚═╗ ║ ║ ║╠╦╝║║║", C.BLUE)
        p("  ╩ ╩╩ ╩╚═╝╩ ╩╚═╝ ╩ ╚═╝╩╚═╩ ╩", C.PURPLE)
        p("     ★ ONLINE EDITION ★", C.GOLD + C.BOLD)
        print()

    def connect_to_server(self):
        """Connect to the game server."""
        self.show_banner()

        # Get server address
        p(f"  Server: {SERVER_HOST}:{SERVER_PORT}", C.STEEL)
        custom = input(f"  {C.CYAN}Custom server? (enter IP or press ENTER for default):{C.RESET} ").strip()

        host = custom if custom else SERVER_HOST
        port = SERVER_PORT

        if ":" in host:
            host, port_str = host.rsplit(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                pass

        p(f"\n  Connecting to {host}:{port}...", C.YELLOW)

        if self.client.connect(host, port):
            p(f"  {C.GREEN}Connected!{C.RESET}")
            time.sleep(1)
            return True
        else:
            p(f"  {C.RED}Failed to connect.{C.RESET}")
            input("  Press ENTER to retry...")
            return False

    def login_menu(self):
        """Login or register."""
        while True:
            clear()
            self.show_banner()

            # Check server info
            info = self.client.simple_request({"action": "info"})
            if info.get("status") == "ok":
                p(f"  {C.STEEL}Server: {info.get('server', 'HackStorm')}{C.RESET}")
                p(f"  {C.STEEL}Players: {info.get('total_players', '?')} registered | {info.get('online', '?')} online{C.RESET}")
            print()

            p(f"  {C.GREEN}1{C.RESET} - Login")
            p(f"  {C.CYAN}2{C.RESET} - Register")
            p(f"  {C.RED}3{C.RESET} - Quit")
            print()

            choice = input(f"  {C.CYAN}>{C.RESET} ").strip()

            if choice == "1":
                result = self.do_login()
                if result:
                    return True
            elif choice == "2":
                self.do_register()
            elif choice == "3":
                self.client.disconnect()
                sys.exit(0)

    def do_login(self):
        """Handle login."""
        print()
        username = input(f"  {C.GREEN}Username:{C.RESET} ").strip()
        password = getpass.getpass(f"  {C.GREEN}Password:{C.RESET} ")

        if not username or not password:
            p("  [ERROR] Both fields required.", C.RED)
            time.sleep(1)
            return False

        p("  Logging in...", C.YELLOW)
        response = self.client.simple_request({
            "action": "login",
            "username": username,
            "password": password,
        })

        if response.get("status") == "ok":
            self.client.username = username
            self.client.game_state = response.get("game_state", {})
            p(f"  {C.GREEN}{response.get('message', 'Welcome!')}{C.RESET}")
            time.sleep(1)
            return True
        else:
            p(f"  {C.RED}{response.get('message', 'Login failed.')}{C.RESET}")
            time.sleep(2)
            return False

    def do_register(self):
        """Handle registration."""
        print()
        username = input(f"  {C.CYAN}Choose username:{C.RESET} ").strip()
        password = getpass.getpass(f"  {C.CYAN}Choose password:{C.RESET} ")
        password2 = getpass.getpass(f"  {C.CYAN}Confirm password:{C.RESET} ")

        if password != password2:
            p("  [ERROR] Passwords don't match.", C.RED)
            time.sleep(1)
            return

        if not username or not password:
            p("  [ERROR] Both fields required.", C.RED)
            time.sleep(1)
            return

        p("  Creating account...", C.YELLOW)
        response = self.client.simple_request({
            "action": "register",
            "username": username,
            "password": password,
        })

        if response.get("status") == "ok":
            p(f"  {C.GREEN}{response.get('message', 'Account created!')}{C.RESET}")
        else:
            p(f"  {C.RED}{response.get('message', 'Registration failed.')}{C.RESET}")
        time.sleep(2)

    def get_prompt(self):
        gs = self.client.game_state or {}
        det = gs.get("detection_level", 0)
        vpn = " [VPN]" if gs.get("vpn_active") else ""
        det_str = f" [DET:{det}%]" if det > 0 else ""
        net = gs.get("current_network", "home") if "current_network" in gs else "home"
        return f"{C.RED}{self.client.username}{C.RESET}@{C.CYAN}{net}{C.RESET}{vpn}{det_str} {C.GREEN}${C.RESET} "

    def show_notifications(self):
        """Display any pending server notifications."""
        notifs = self.client.get_notifications()
        for n in notifs:
            if n.get("type") == "notification":
                p(f"  {C.YELLOW}{n.get('message', '')}{C.RESET}")
            elif n.get("type") == "chat":
                data = n.get("data", {})
                p(f"  {C.STEEL}[{data.get('time', '')}]{C.RESET} {C.CYAN}{data.get('user', '?')}{C.RESET}: {data.get('text', '')}")

    def cmd_online(self):
        """Show who's online."""
        response = self.client.simple_request({"action": "online"})
        if response.get("status") == "ok":
            players = response.get("players", [])
            print()
            p(f"  {C.BOLD}Online Players ({response.get('count', 0)}):{C.RESET}")
            if players:
                for pl in players:
                    p(f"    {C.GREEN}●{C.RESET} {C.BOLD}{pl['name']}{C.RESET} (Lvl {pl['level']})")
            else:
                p("    No one else is online.", C.DIM)
            print()
        else:
            p(f"  {C.RED}{response.get('message', 'Error')}{C.RESET}")

    def cmd_chat(self, args):
        """Send a chat message."""
        if not args:
            p("  [USAGE] chat <message>", C.YELLOW)
            return
        message = " ".join(args)
        response = self.client.simple_request({
            "action": "chat",
            "username": self.client.username,
            "message": message,
        })
        if response.get("status") == "ok":
            p(f"  {C.STEEL}[{time.strftime('%H:%M:%S')}]{C.RESET} {C.CYAN}{self.client.username}{C.RESET}: {message}")
        else:
            p(f"  {C.RED}{response.get('message', 'Failed')}{C.RESET}")

    def cmd_chatlog(self):
        """View chat history."""
        response = self.client.simple_request({
            "action": "chat_history",
            "count": 20,
        })
        if response.get("status") == "ok":
            messages = response.get("messages", [])
            print()
            p(f"  {C.BOLD}Chat History (last {len(messages)}):{C.RESET}")
            if messages:
                for msg in messages:
                    p(f"  {C.STEEL}[{msg.get('time', '')}]{C.RESET} {C.CYAN}{msg.get('user', '?')}{C.RESET}: {msg.get('text', '')}")
            else:
                p("  No messages yet.", C.DIM)
            print()

    def cmd_leaderboard(self):
        """Show global leaderboard."""
        clear()
        response = self.client.simple_request({
            "action": "leaderboard",
            "sort_by": "reputation",
        })
        if response.get("status") == "ok":
            lb = response.get("leaderboard", [])
            print()
            p(f"  {C.GOLD}{C.BOLD}=== GLOBAL LEADERBOARD ==={C.RESET}")
            print()
            rank_colors = [C.GOLD, C.STEEL, C.ORANGE]
            p(f"  {'RANK':<6}{'HACKER':<18}{'REP':<10}{'LVL':<6}{'$$$':<12}{'STATUS'}", C.BOLD)
            for i, entry in enumerate(lb):
                rc = rank_colors[i] if i < 3 else C.WHITE
                online = f"{C.GREEN}ONLINE{C.RESET}" if entry.get("online") else f"{C.DIM}offline{C.RESET}"
                you = f" {C.PINK}<- YOU{C.RESET}" if entry["name"] == self.client.username else ""
                p(f"  {rc}{i+1:<6}{C.RESET}{C.BOLD}{entry['name']:<18}{C.RESET}"
                  f"{C.MAGENTA}{entry.get('reputation', 0):<10}{C.RESET}"
                  f"{entry.get('level', 1):<6}"
                  f"{C.GOLD}${entry.get('money', 0):,}{C.RESET}{'':>4}"
                  f"{online}{you}")
            print()
        else:
            p(f"  {C.RED}{response.get('message', 'Error')}{C.RESET}")

    def cmd_profile(self, args):
        """View a player's profile."""
        if not args:
            p("  [USAGE] profile <username>", C.YELLOW)
            return
        target = args[0]
        response = self.client.simple_request({
            "action": "profile",
            "target": target,
        })
        if response.get("status") == "ok":
            prof = response.get("profile", {})
            print()
            online = f"{C.GREEN}ONLINE{C.RESET}" if prof.get("online") else f"{C.RED}OFFLINE{C.RESET}"
            p(f"  {C.BOLD}=== {prof.get('name', '?')} ==={C.RESET}  {online}")
            p(f"  Level:      {prof.get('level', 1)}")
            p(f"  Money:      ${prof.get('money', 0):,}")
            p(f"  Reputation: {prof.get('reputation', 0)}")
            p(f"  Missions:   {prof.get('missions', 0)}")
            p(f"  Tools:      {prof.get('tools', 0)}")
            p(f"  Created:    {prof.get('created', '?')}")
            p(f"  Last login: {prof.get('last_login', '?')}")
            p(f"  Total logins: {prof.get('total_logins', 0)}")
            print()
        else:
            p(f"  {C.RED}{response.get('message', 'Not found')}{C.RESET}")

    def cmd_save(self):
        """Save game to server."""
        response = self.client.simple_request({
            "action": "save",
            "username": self.client.username,
            "game_state": self.client.game_state,
        })
        if response.get("status") == "ok":
            p(f"  {C.GREEN}Game saved to server!{C.RESET}")
        else:
            p(f"  {C.RED}{response.get('message', 'Save failed')}{C.RESET}")

    def auto_save(self):
        self.auto_save_counter += 1
        if self.auto_save_counter % 10 == 0:
            try:
                self.client.simple_request({
                    "action": "save",
                    "username": self.client.username,
                    "game_state": self.client.game_state,
                })
            except Exception:
                pass

    def cmd_help_online(self):
        """Show online-specific commands."""
        print()
        p(f"  {C.BOLD}{C.GOLD}=== ONLINE COMMANDS ==={C.RESET}")
        print()
        p(f"    {C.GREEN}online{C.RESET}              See who's online")
        p(f"    {C.GREEN}chat <message>{C.RESET}      Send chat message")
        p(f"    {C.GREEN}chatlog{C.RESET}             View chat history")
        p(f"    {C.GREEN}leaderboard{C.RESET}         Global rankings")
        p(f"    {C.GREEN}profile <name>{C.RESET}      View player profile")
        p(f"    {C.GREEN}save{C.RESET}                Save to server")
        p(f"    {C.GREEN}serverinfo{C.RESET}          Server information")
        p(f"    {C.GREEN}logout{C.RESET}              Logout and quit")
        print()
        p("  All normal game commands also work!", C.DIM)
        p("  Type 'help' for full command list.", C.DIM)
        print()

    def cmd_serverinfo(self):
        response = self.client.simple_request({"action": "info"})
        if response.get("status") == "ok":
            print()
            p(f"  {C.BOLD}Server Info:{C.RESET}")
            p(f"    Name:    {response.get('server', '?')}")
            p(f"    Players: {response.get('total_players', '?')} registered")
            p(f"    Online:  {response.get('online', '?')}")
            print()

    def process_online_command(self, raw_input):
        """Handle online-specific commands."""
        parts = raw_input.strip().split()
        if not parts:
            return False
        cmd = parts[0].lower()
        args = parts[1:]

        online_commands = {
            "online": lambda: self.cmd_online(),
            "chat": lambda: self.cmd_chat(args),
            "chatlog": lambda: self.cmd_chatlog(),
            "leaderboard": lambda: self.cmd_leaderboard(),
            "profile": lambda: self.cmd_profile(args),
            "save": lambda: self.cmd_save(),
            "serverinfo": lambda: self.cmd_serverinfo(),
            "ohelp": lambda: self.cmd_help_online(),
            "logout": lambda: self.do_logout(),
        }

        if cmd in online_commands:
            online_commands[cmd]()
            self.auto_save()
            return True
        return False

    def do_logout(self):
        p("  Saving and logging out...", C.YELLOW)
        self.client.disconnect()
        p(f"  {C.GREEN}Goodbye, {self.client.username}!{C.RESET}")
        time.sleep(1)
        sys.exit(0)

    def run(self):
        """Main client loop."""
        clear()
        self.show_banner()

        # Connect
        while not self.client.connected:
            if not self.connect_to_server():
                continue

        # Login
        if not self.login_menu():
            return

        # Main game loop
        clear()
        self.show_banner()
        p(f"  Logged in as: {C.BOLD}{C.CYAN}{self.client.username}{C.RESET}")
        p(f"  Type {C.GREEN}'ohelp'{C.RESET} for online commands")
        p(f"  Type {C.GREEN}'help'{C.RESET} for game commands")
        print()

        while self.running:
            try:
                # Show any notifications from server
                self.show_notifications()

                prompt = self.get_prompt()
                user_input = input(prompt)

                if not user_input.strip():
                    continue

                # Try online commands first
                if self.process_online_command(user_input):
                    continue

                # Otherwise handle as local game command
                p(f"  {C.DIM}[Local command - game runs locally, progress syncs to server]{C.RESET}")
                p(f"  {C.YELLOW}Game commands work the same as offline mode.{C.RESET}")
                p(f"  {C.DIM}Type 'ohelp' for online commands.{C.RESET}")

            except KeyboardInterrupt:
                print(f"\n  {C.YELLOW}Use 'logout' to quit.{C.RESET}\n")
            except EOFError:
                self.do_logout()


# ============================================================
#                       START
# ============================================================
if __name__ == "__main__":
    game = HackStormOnline()
    game.run()