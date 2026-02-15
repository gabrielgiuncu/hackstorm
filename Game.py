import time
import random
import sys
import os
import getpass
import hashlib
import json
import pathlib

# ============================================================
#               CROSS-PLATFORM ANSI COLOR SYSTEM
# ============================================================

def enable_ansi():
    """Enable ANSI colors on all platforms including Windows CMD, Termux, etc."""
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            pass
        # Windows Terminal, VS Code, etc.
        if any(os.environ.get(v) for v in ['WT_SESSION', 'TERM_PROGRAM', 'ANSICON']):
            return True
        # Try anyway on modern Windows
        try:
            os.system('')  # This can enable ANSI on some Windows versions
            return True
        except Exception:
            return False
    else:
        # Linux, Mac, Termux, Android - always support ANSI
        return True

USE_COLORS = enable_ansi()

class C:
    """ANSI Color codes with rich color palette."""
    if USE_COLORS:
        # Standard colors
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"

        # Bright / Light colors
        LRED = "\033[91m"
        LGREEN = "\033[92m"
        LYELLOW = "\033[93m"
        LBLUE = "\033[94m"
        LMAGENTA = "\033[95m"
        LCYAN = "\033[96m"
        LWHITE = "\033[97m"

        # 256-color extended palette
        ORANGE = "\033[38;5;208m"
        PINK = "\033[38;5;205m"
        PURPLE = "\033[38;5;129m"
        LIME = "\033[38;5;118m"
        TEAL = "\033[38;5;30m"
        GOLD = "\033[38;5;220m"
        SILVER = "\033[38;5;250m"
        NAVY = "\033[38;5;17m"
        CRIMSON = "\033[38;5;196m"
        EMERALD = "\033[38;5;46m"
        VIOLET = "\033[38;5;135m"
        RUST = "\033[38;5;166m"
        SKY = "\033[38;5;117m"
        CORAL = "\033[38;5;209m"
        MINT = "\033[38;5;121m"
        LAVENDER = "\033[38;5;183m"
        BRONZE = "\033[38;5;136m"
        STEEL = "\033[38;5;244m"
        NEON_GREEN = "\033[38;5;46m"
        NEON_BLUE = "\033[38;5;27m"
        NEON_PINK = "\033[38;5;198m"
        NEON_YELLOW = "\033[38;5;226m"
        DARK_RED = "\033[38;5;88m"
        DARK_GREEN = "\033[38;5;22m"
        DARK_BLUE = "\033[38;5;18m"
        DARK_CYAN = "\033[38;5;23m"

        # Background colors
        BG_BLACK = "\033[40m"
        BG_RED = "\033[41m"
        BG_GREEN = "\033[42m"
        BG_YELLOW = "\033[43m"
        BG_BLUE = "\033[44m"
        BG_MAGENTA = "\033[45m"
        BG_CYAN = "\033[46m"
        BG_WHITE = "\033[47m"
        BG_ORANGE = "\033[48;5;208m"
        BG_PURPLE = "\033[48;5;129m"
        BG_DARK = "\033[48;5;235m"
        BG_DARK_GREEN = "\033[48;5;22m"
        BG_DARK_RED = "\033[48;5;52m"
        BG_DARK_BLUE = "\033[48;5;17m"

        # Styles
        BOLD = "\033[1m"
        DIM = "\033[2m"
        ITALIC = "\033[3m"
        UNDERLINE = "\033[4m"
        BLINK = "\033[5m"
        INVERSE = "\033[7m"
        STRIKETHROUGH = "\033[9m"
        RESET = "\033[0m"
    else:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
        LRED = LGREEN = LYELLOW = LBLUE = LMAGENTA = LCYAN = LWHITE = ""
        ORANGE = PINK = PURPLE = LIME = TEAL = GOLD = SILVER = ""
        NAVY = CRIMSON = EMERALD = VIOLET = RUST = SKY = CORAL = ""
        MINT = LAVENDER = BRONZE = STEEL = ""
        NEON_GREEN = NEON_BLUE = NEON_PINK = NEON_YELLOW = ""
        DARK_RED = DARK_GREEN = DARK_BLUE = DARK_CYAN = ""
        BG_BLACK = BG_RED = BG_GREEN = BG_YELLOW = BG_BLUE = ""
        BG_MAGENTA = BG_CYAN = BG_WHITE = BG_ORANGE = BG_PURPLE = ""
        BG_DARK = BG_DARK_GREEN = BG_DARK_RED = BG_DARK_BLUE = ""
        BOLD = DIM = ITALIC = UNDERLINE = BLINK = INVERSE = STRIKETHROUGH = ""
        RESET = ""

    @staticmethod
    def rgb(r, g, b):
        """Create custom RGB foreground color."""
        if USE_COLORS:
            return f"\033[38;2;{r};{g};{b}m"
        return ""

    @staticmethod
    def bg_rgb(r, g, b):
        """Create custom RGB background color."""
        if USE_COLORS:
            return f"\033[48;2;{r};{g};{b}m"
        return ""

    @staticmethod
    def color256(n):
        """Use 256-color palette."""
        if USE_COLORS:
            return f"\033[38;5;{n}m"
        return ""

    @staticmethod
    def gradient_text(text, start_color, end_color):
        """Create gradient text between two RGB colors."""
        if not USE_COLORS:
            return text
        result = ""
        length = max(len(text), 1)
        for i, char in enumerate(text):
            ratio = i / length
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            result += f"\033[38;2;{r};{g};{b}m{char}"
        return result + "\033[0m"


def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


# ============================================================
#                SAVE / LOAD SYSTEM
# ============================================================

GAME_DIR = os.path.join(pathlib.Path.home(), ".hackstorm")
PROFILES_DIR = os.path.join(GAME_DIR, "profiles")

def ensure_game_dirs():
    """Create game directories if they don't exist."""
    os.makedirs(GAME_DIR, exist_ok=True)
    os.makedirs(PROFILES_DIR, exist_ok=True)

def get_user_dir(username):
    """Get the directory for a specific user."""
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in username)
    user_dir = os.path.join(PROFILES_DIR, safe_name)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def save_game(state, missions, username):
    """Save game state to user's folder."""
    user_dir = get_user_dir(username)
    save_data = {
        "version": "2.0",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "player": {
            "name": state.player_name,
            "reputation": state.reputation,
            "money": state.money,
            "level": state.level,
            "xp": state.xp,
            "xp_to_next": state.xp_to_next,
            "tools": state.tools,
            "files": state.files,
            "ip_address": state.ip_address,
            "vpn_active": state.vpn_active,
            "proxy_chains": state.proxy_chains,
            "botnet_size": state.botnet_size,
            "detection_level": state.detection_level,
            "crypto_wallet": state.crypto_wallet,
            "notes": state.notes,
            "tutorial_done": state.tutorial_done,
        },
        "progress": {
            "known_passwords": state.known_passwords,
            "backdoors": state.backdoors,
            "log_cleaned": state.log_cleaned,
            "intercepted_data": state.intercepted_data,
            "completed_missions": state.completed_missions,
            "compromised_targets": [
                ip for ip, t in state.available_targets.items() if t["compromised"]
            ],
        },
        "missions": [
            {"id": m["id"], "completed": m["completed"]}
            for m in missions.missions
        ],
        "stats": {
            "total_money_earned": state.money + sum(
                m["reward_money"] for m in missions.missions if m["completed"]
            ),
            "targets_hacked": len([t for t in state.available_targets.values() if t["compromised"]]),
            "missions_completed": len(state.completed_missions),
        }
    }

    save_path = os.path.join(user_dir, "save.json")
    try:
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)

        # Also save a human-readable stats file
        stats_path = os.path.join(user_dir, "stats.txt")
        with open(stats_path, 'w') as f:
            f.write(f"=== HackStorm Profile: {state.player_name} ===\n")
            f.write(f"Last saved: {save_data['timestamp']}\n")
            f.write(f"Level: {state.level}\n")
            f.write(f"Money: ${state.money:,}\n")
            f.write(f"Crypto: {state.crypto_wallet:.6f} BTC\n")
            f.write(f"Reputation: {state.reputation}\n")
            f.write(f"Missions: {len(state.completed_missions)}/{len(missions.missions)}\n")
            f.write(f"Tools: {', '.join(state.tools)}\n")
            f.write(f"Files: {', '.join(state.files)}\n")

        # Save command history log
        history_path = os.path.join(user_dir, "history.log")
        with open(history_path, 'a') as f:
            f.write(f"\n--- Session {save_data['timestamp']} ---\n")

        return True
    except Exception as e:
        return False


def load_game(username):
    """Load game state from user's folder."""
    user_dir = get_user_dir(username)
    save_path = os.path.join(user_dir, "save.json")

    if not os.path.exists(save_path):
        return None

    try:
        with open(save_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception:
        return None


def list_profiles():
    """List all saved profiles."""
    ensure_game_dirs()
    profiles = []
    if os.path.exists(PROFILES_DIR):
        for name in os.listdir(PROFILES_DIR):
            user_dir = os.path.join(PROFILES_DIR, name)
            save_path = os.path.join(user_dir, "save.json")
            if os.path.isdir(user_dir) and os.path.exists(save_path):
                try:
                    with open(save_path, 'r') as f:
                        data = json.load(f)
                    profiles.append({
                        "folder": name,
                        "name": data["player"]["name"],
                        "level": data["player"]["level"],
                        "money": data["player"]["money"],
                        "timestamp": data.get("timestamp", "unknown"),
                        "missions": data["stats"]["missions_completed"],
                        "total_missions": len(data["missions"]),
                    })
                except Exception:
                    pass
    return profiles


def delete_profile(username):
    """Delete a user's profile folder."""
    user_dir = get_user_dir(username)
    if os.path.exists(user_dir):
        import shutil
        shutil.rmtree(user_dir)
        return True
    return False


def save_command_to_history(username, command):
    """Append command to user's history log."""
    user_dir = get_user_dir(username)
    history_path = os.path.join(user_dir, "history.log")
    try:
        with open(history_path, 'a') as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] {command}\n")
    except Exception:
        pass


# ============================================================
#                    TEXT EFFECTS
# ============================================================

def p(text, color=""):
    """Print with color (short helper)."""
    if USE_COLORS and color:
        print(color + text + C.RESET)
    else:
        print(text)

def type_text(text, speed=0.03, color=""):
    c = color if USE_COLORS else ""
    r = C.RESET if USE_COLORS else ""
    for char in text:
        sys.stdout.write(c + char + r)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def type_loading(message, duration=2):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    # Fallback for terminals without unicode
    try:
        "⠋".encode(sys.stdout.encoding or 'utf-8')
    except (UnicodeEncodeError, LookupError):
        frames = ["|", "/", "-", "\\"]

    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r  {C.CYAN}{frame}{C.RESET} {message}...")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write(f"\r  {C.LGREEN}+{C.RESET} {message}... {C.LGREEN}OK{C.RESET}\n")
    sys.stdout.flush()

def progress_bar(message, duration=2, width=40):
    p(f"  {message}", C.LYELLOW)
    for i in range(width + 1):
        percent = (i / width) * 100
        filled_color = C.LGREEN if percent < 50 else (C.LYELLOW if percent < 80 else C.LRED)
        bar = f"{filled_color}{'█' * i}{C.STEEL}{'░' * (width - i)}{C.RESET}"
        try:
            sys.stdout.write(f"\r  [{bar}] {C.LWHITE}{percent:.0f}%{C.RESET}")
        except UnicodeEncodeError:
            filled = "#" * i
            empty = "-" * (width - i)
            sys.stdout.write(f"\r  [{filled}{empty}] {percent:.0f}%")
        sys.stdout.flush()
        time.sleep(duration / width)
    print()

def hacker_progress_bar(message, duration=2, width=40):
    p(f"  {message}", C.LYELLOW)
    hex_chars = "0123456789ABCDEF"
    for i in range(width + 1):
        percent = (i / width) * 100
        try:
            bar = f"{C.NEON_GREEN}{'█' * i}{C.STEEL}{'░' * (width - i)}{C.RESET}"
        except Exception:
            bar = f"{'#' * i}{'-' * (width - i)}"
        leak = ''.join(random.choices(hex_chars, k=8))
        try:
            sys.stdout.write(f"\r  [{bar}] {C.LWHITE}{percent:.0f}%{C.RESET} {C.DIM}{C.GREEN}0x{leak}{C.RESET}")
        except UnicodeEncodeError:
            sys.stdout.write(f"\r  [{'#' * i}{'-' * (width - i)}] {percent:.0f}% 0x{leak}")
        sys.stdout.flush()
        time.sleep(duration / width)
    print()

def fake_data_stream(lines=15, speed=0.05):
    hex_chars = "0123456789ABCDEF"
    colors = [C.GREEN, C.DARK_GREEN, C.LGREEN, C.EMERALD, C.MINT, C.TEAL]
    for _ in range(lines):
        addr = ''.join(random.choices(hex_chars, k=8))
        data = ' '.join(''.join(random.choices(hex_chars, k=2)) for _ in range(16))
        color = random.choice(colors)
        p(f"  {C.DIM}{color}0x{addr}  {data}{C.RESET}")
        time.sleep(speed)

def matrix_rain(duration=3):
    chars = "01"
    width = min(70, os.get_terminal_size().columns - 2) if hasattr(os, 'get_terminal_size') else 70
    colors = [C.GREEN, C.LGREEN, C.DARK_GREEN, C.EMERALD, C.NEON_GREEN]
    end_time = time.time() + duration
    while time.time() < end_time:
        line = ''.join(random.choices(chars, weights=[3, 1], k=width))
        color = random.choice(colors)
        p(line, C.DIM + color)
        time.sleep(0.04)

def glitch_text(text, iterations=6, speed=0.08):
    glitch_chars = "@#$%&*!?><{}[]=/\\|~^"
    colors = [C.LRED, C.LGREEN, C.LCYAN, C.LYELLOW, C.LMAGENTA, C.ORANGE]
    for i in range(iterations):
        glitched = ""
        color = random.choice(colors)
        for j, char in enumerate(text):
            if char == " ":
                glitched += " "
            elif random.random() < (i / iterations):
                glitched += char
            else:
                glitched += random.choice(glitch_chars)
        sys.stdout.write(f"\r{color}{glitched}{C.RESET}")
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write(f"\r{C.BOLD}{C.LCYAN}{text}{C.RESET}\n")
    sys.stdout.flush()

def typing_animation(text, speed=0.04):
    for i in range(len(text) + 1):
        sys.stdout.write(f"\r  {C.LGREEN}>{C.RESET} {text[:i]}{C.LGREEN}_{C.RESET}")
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write(f"\r  {C.LGREEN}>{C.RESET} {text} \n")
    sys.stdout.flush()

def scan_animation(target, duration=2):
    scan_items = [
        "Checking open ports",
        "Analyzing services",
        "Fingerprinting OS",
        "Detecting firewall",
        "Mapping network",
        "Identifying vulnerabilities",
    ]
    for item in scan_items:
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        try:
            "⠋".encode(sys.stdout.encoding or 'utf-8')
        except (UnicodeEncodeError, LookupError):
            frames = ["|", "/", "-", "\\"]
        end_time = time.time() + (duration / len(scan_items))
        i = 0
        while time.time() < end_time:
            frame = frames[i % len(frames)]
            sys.stdout.write(f"\r  {C.CYAN}{frame}{C.RESET} {item}...")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        sys.stdout.write(f"\r  {C.LGREEN}+{C.RESET} {item}... {C.LGREEN}DONE{C.RESET}\n")
        sys.stdout.flush()

def decrypt_animation(text, speed=0.03):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%"
    display = list(''.join(random.choices(chars, k=len(text))))
    for iteration in range(len(text)):
        display[iteration] = text[iteration]
        for j in range(iteration + 1, len(text)):
            if text[j] != ' ':
                display[j] = random.choice(chars)
            else:
                display[j] = ' '
        sys.stdout.write(f"\r  {C.LGREEN}{''.join(display)}{C.RESET}")
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write(f"\r  {text}{C.RESET}\n")
    sys.stdout.flush()

def warning_flash(message, flashes=3):
    for _ in range(flashes):
        sys.stdout.write(f"\r  {C.BG_RED}{C.LWHITE}{C.BOLD} [!!!] {message} [!!!] {C.RESET}")
        sys.stdout.flush()
        time.sleep(0.3)
        sys.stdout.write(f"\r{' ' * (len(message) + 25)}\r")
        sys.stdout.flush()
        time.sleep(0.2)
    p(f"  {C.BG_RED}{C.LWHITE}{C.BOLD} [!!!] {message} [!!!] {C.RESET}")

def password_crack_animation(password, duration=3):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    display = ["_"] * len(password)
    delay = duration / len(password)

    for i in range(len(password)):
        for _ in range(random.randint(5, 15)):
            display[i] = random.choice(chars)
            cracked = f"{C.LGREEN}{''.join(display[:i])}{C.RESET}"
            current = f"{C.LYELLOW}{display[i]}{C.RESET}"
            remaining = f"{C.STEEL}{''.join(display[i+1:])}{C.RESET}"
            sys.stdout.write(f"\r  Password: [{cracked}{current}{remaining}]")
            sys.stdout.flush()
            time.sleep(0.02)
        display[i] = password[i]
        time.sleep(delay)

    final = f"{C.LGREEN}{C.BOLD}{''.join(display)}{C.RESET}"
    sys.stdout.write(f"\r  Password: [{final}]")
    sys.stdout.flush()
    print()

def rainbow_text(text):
    """Print text with rainbow colors."""
    colors = [C.LRED, C.ORANGE, C.LYELLOW, C.LGREEN, C.LCYAN, C.LBLUE, C.LMAGENTA]
    result = ""
    for i, char in enumerate(text):
        if char == " ":
            result += " "
        else:
            result += colors[i % len(colors)] + char
    print(result + C.RESET)

def gradient_print(text, start_rgb, end_rgb):
    """Print text with RGB gradient."""
    print(C.gradient_text(text, start_rgb, end_rgb))

def fire_text(text):
    """Print text with fire colors."""
    fire_colors = [
        C.rgb(255, 0, 0), C.rgb(255, 69, 0), C.rgb(255, 140, 0),
        C.rgb(255, 165, 0), C.rgb(255, 200, 0), C.rgb(255, 255, 0),
    ]
    result = ""
    for i, char in enumerate(text):
        result += fire_colors[i % len(fire_colors)] + char
    print(result + C.RESET)

def ice_text(text):
    """Print text with ice/frost colors."""
    ice_colors = [
        C.rgb(200, 230, 255), C.rgb(150, 200, 255), C.rgb(100, 170, 255),
        C.rgb(50, 140, 255), C.rgb(0, 110, 255), C.rgb(0, 80, 200),
    ]
    result = ""
    for i, char in enumerate(text):
        result += ice_colors[i % len(ice_colors)] + char
    print(result + C.RESET)

def neon_box(text, color=None):
    """Draw a neon-style box around text."""
    if color is None:
        color = C.LCYAN
    width = len(text) + 4
    p(f"  {color}{'━' * width}{C.RESET}")
    p(f"  {color}┃{C.RESET} {C.BOLD}{C.LWHITE}{text}{C.RESET} {color}┃{C.RESET}")
    p(f"  {color}{'━' * width}{C.RESET}")

def double_box(lines, title="", color=None):
    """Draw a double-line box with optional title."""
    if color is None:
        color = C.LCYAN
    max_width = max(len(line) for line in lines) if lines else 20
    max_width = max(max_width, len(title)) + 4
    top = f"╔{'═' * max_width}╗"
    bottom = f"╚{'═' * max_width}╝"
    p(f"  {color}{top}{C.RESET}")
    if title:
        padding = max_width - len(title) - 2
        p(f"  {color}║{C.RESET} {C.BOLD}{C.LWHITE}{title}{C.RESET}{' ' * padding}{color} ║{C.RESET}")
        p(f"  {color}╠{'═' * max_width}╣{C.RESET}")
    for line in lines:
        padding = max_width - len(line) - 2
        p(f"  {color}║{C.RESET} {line}{' ' * padding}{color} ║{C.RESET}")
    p(f"  {color}{bottom}{C.RESET}")

def network_map_animation():
    print()
    p("  Mapping network topology...", C.LYELLOW)
    time.sleep(0.5)
    map_lines = [
        (f"                    {C.LRED}[INTERNET]{C.RESET}", 0.3),
        (f"                        {C.STEEL}|{C.RESET}", 0.1),
        (f"                    {C.ORANGE}[GATEWAY]{C.RESET}", 0.3),
        (f"                   {C.STEEL}/    |    \\{C.RESET}", 0.1),
        (f"              {C.LYELLOW}[DMZ]{C.RESET}  {C.LGREEN}[LAN]{C.RESET}  {C.LCYAN}[WIFI]{C.RESET}", 0.3),
        (f"              {C.STEEL}/   \\    |      |{C.RESET}", 0.1),
        (f"          {C.LRED}[WEB]{C.RESET} {C.LBLUE}[DNS]{C.RESET} {C.LMAGENTA}[DB]{C.RESET}  {C.PURPLE}[IoT]{C.RESET}", 0.3),
        (f"            {C.STEEL}|           |{C.RESET}", 0.1),
        (f"         {C.GOLD}[LOGS]{C.RESET}      {C.EMERALD}[BACKUP]{C.RESET}", 0.3),
    ]
    for line, delay in map_lines:
        print(line)
        time.sleep(delay)
    print()


# ============================================================
#                      GAME STATE
# ============================================================

class GameState:
    def __init__(self):
        self.player_name = "ghost"
        self.reputation = 0
        self.money = 1000  # Start with $1000 as requested
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        self.tools = ["nmap", "ping"]
        self.files = ["readme.txt", "notes.txt"]
        self.completed_missions = []
        self.current_network = "home"
        self.connected_to = None
        self.firewall_bypassed = False
        self.detected = False
        self.detection_level = 0
        self.ip_address = f"192.168.1.{random.randint(2, 254)}"
        self.vpn_active = False
        self.proxy_chains = 0
        self.botnet_size = 0
        self.known_passwords = {}
        self.intercepted_data = []
        self.backdoors = []
        self.log_cleaned = []
        self.tutorial_done = False
        self.crypto_wallet = 0.0
        self.notes = []
        self.available_targets = self._generate_targets()
        self.shop_items = {
            "hydra":        {"price": 300,  "desc": "Brute-force password cracker",      "type": "tool"},
            "sqlmap":       {"price": 500,  "desc": "SQL injection tool",                "type": "tool"},
            "metasploit":   {"price": 800,  "desc": "Exploitation framework",            "type": "tool"},
            "wireshark":    {"price": 400,  "desc": "Packet sniffer / analyzer",         "type": "tool"},
            "john":         {"price": 350,  "desc": "Password hash cracker",             "type": "tool"},
            "aircrack":     {"price": 600,  "desc": "WiFi network cracker",              "type": "tool"},
            "rootkit":      {"price": 1000, "desc": "Persistent backdoor kit",           "type": "tool"},
            "vpn":          {"price": 200,  "desc": "Hide your real IP address",         "type": "service"},
            "proxy_chain":  {"price": 150,  "desc": "Add a proxy layer (+1)",            "type": "service"},
            "botnet_node":  {"price": 500,  "desc": "Add 10 bots to botnet",             "type": "service"},
            "ram_upgrade":  {"price": 400,  "desc": "Faster cracking speed",             "type": "upgrade"},
            "zero_day":     {"price": 2000, "desc": "Bypass any firewall",               "type": "tool"},
            "crypto_miner": {"price": 750,  "desc": "Mine crypto on targets",            "type": "tool"},
            "social_eng":   {"price": 450,  "desc": "Social engineering toolkit",        "type": "tool"},
            "ddos_cannon":  {"price": 1200, "desc": "DDoS attack tool",                  "type": "tool"},
            "forensics":    {"price": 600,  "desc": "Digital forensics toolkit",         "type": "tool"},
        }

    def _generate_targets(self):
        return {
            "192.168.1.1": {
                "name": "Home Router", "difficulty": 1, "os": "Linux 2.6",
                "ports": {22: "SSH", 80: "HTTP", 443: "HTTPS"},
                "firewall": False, "firewall_level": 0,
                "password_hash": hashlib.md5(b"admin123").hexdigest(),
                "password": "admin123",
                "loot": {"money": 100, "xp": 25, "files": ["router_config.txt"]},
                "compromised": False, "services": ["SSH", "HTTP"],
            },
            "10.0.0.5": {
                "name": "Small Business Server", "difficulty": 2, "os": "Windows Server 2016",
                "ports": {21: "FTP", 22: "SSH", 80: "HTTP", 3306: "MySQL"},
                "firewall": True, "firewall_level": 1,
                "password_hash": hashlib.md5(b"P@ssw0rd").hexdigest(),
                "password": "P@ssw0rd",
                "loot": {"money": 500, "xp": 75, "files": ["customer_db.sql", "emails.txt"]},
                "compromised": False, "services": ["FTP", "SSH", "HTTP", "MySQL"],
            },
            "172.16.0.10": {
                "name": "University Database", "difficulty": 3, "os": "Ubuntu 20.04",
                "ports": {22: "SSH", 80: "HTTP", 443: "HTTPS", 5432: "PostgreSQL"},
                "firewall": True, "firewall_level": 2,
                "password_hash": hashlib.md5(b"academic2024").hexdigest(),
                "password": "academic2024",
                "loot": {"money": 1000, "xp": 150, "files": ["student_records.db", "research_data.zip"]},
                "compromised": False, "services": ["SSH", "HTTP", "HTTPS", "PostgreSQL"],
            },
            "198.51.100.20": {
                "name": "Dark Web Marketplace", "difficulty": 3, "os": "Tor Hidden (Debian)",
                "ports": {80: "HTTP", 443: "HTTPS", 6667: "IRC"},
                "firewall": True, "firewall_level": 2,
                "password_hash": hashlib.md5(b"darkn3t!").hexdigest(),
                "password": "darkn3t!",
                "loot": {"money": 5000, "xp": 200, "files": ["market_users.db", "crypto_wallets.dat"]},
                "compromised": False, "services": ["HTTP", "HTTPS", "IRC"],
            },
            "10.10.10.1": {
                "name": "Corporate - MegaCorp", "difficulty": 4, "os": "Windows Server 2019",
                "ports": {22: "SSH", 80: "HTTP", 443: "HTTPS", 445: "SMB", 1433: "MSSQL", 3389: "RDP"},
                "firewall": True, "firewall_level": 3,
                "password_hash": hashlib.md5(b"C0rp$ecure!").hexdigest(),
                "password": "C0rp$ecure!",
                "loot": {"money": 3000, "xp": 300, "files": ["financial_reports.xlsx", "employee_data.csv", "trade_secrets.doc"]},
                "compromised": False, "services": ["SSH", "HTTP", "HTTPS", "SMB", "MSSQL", "RDP"],
            },
            "10.20.30.40": {
                "name": "Government - ClassifiedNet", "difficulty": 5, "os": "Hardened Linux (SELinux)",
                "ports": {22: "SSH", 443: "HTTPS", 8443: "Secure Portal"},
                "firewall": True, "firewall_level": 5,
                "password_hash": hashlib.md5(b"T0p$3cr3t!Gov").hexdigest(),
                "password": "T0p$3cr3t!Gov",
                "loot": {"money": 10000, "xp": 1000, "files": ["classified_intel.enc", "agent_list.gpg", "operation_files.tar.gz"]},
                "compromised": False, "services": ["SSH", "HTTPS", "Secure Portal"],
            },
            "203.0.113.50": {
                "name": "Bank of CyberCity", "difficulty": 5, "os": "AIX 7.2",
                "ports": {22: "SSH", 443: "HTTPS", 8080: "API Gateway", 9090: "Admin Panel"},
                "firewall": True, "firewall_level": 4,
                "password_hash": hashlib.md5(b"B@nkV4ult!").hexdigest(),
                "password": "B@nkV4ult!",
                "loot": {"money": 25000, "xp": 1500, "files": ["transaction_logs.db", "account_data.enc"]},
                "compromised": False, "services": ["SSH", "HTTPS", "API Gateway", "Admin Panel"],
            },
            "10.99.99.1": {
                "name": "Satellite Comm System", "difficulty": 5, "os": "VxWorks RTOS",
                "ports": {22: "SSH", 8080: "Control Panel", 9999: "Telemetry"},
                "firewall": True, "firewall_level": 5,
                "password_hash": hashlib.md5(b"0rb1t@lC0mm").hexdigest(),
                "password": "0rb1t@lC0mm",
                "loot": {"money": 50000, "xp": 3000, "files": ["sat_telemetry.dat", "comm_encryption.key", "orbital_data.bin"]},
                "compromised": False, "services": ["SSH", "Control Panel", "Telemetry"],
            },
        }

    def apply_save(self, data):
        """Apply loaded save data to this state."""
        pl = data["player"]
        self.player_name = pl["name"]
        self.reputation = pl.get("reputation", 0)
        self.money = pl.get("money", 1000)
        self.level = pl.get("level", 1)
        self.xp = pl.get("xp", 0)
        self.xp_to_next = pl.get("xp_to_next", 100)
        self.tools = pl.get("tools", ["nmap", "ping"])
        self.files = pl.get("files", ["readme.txt", "notes.txt"])
        self.ip_address = pl.get("ip_address", self.ip_address)
        self.vpn_active = pl.get("vpn_active", False)
        self.proxy_chains = pl.get("proxy_chains", 0)
        self.botnet_size = pl.get("botnet_size", 0)
        self.detection_level = pl.get("detection_level", 0)
        self.crypto_wallet = pl.get("crypto_wallet", 0.0)
        self.notes = pl.get("notes", [])
        self.tutorial_done = pl.get("tutorial_done", False)

        prog = data.get("progress", {})
        self.known_passwords = prog.get("known_passwords", {})
        self.backdoors = prog.get("backdoors", [])
        self.log_cleaned = prog.get("log_cleaned", [])
        self.intercepted_data = prog.get("intercepted_data", [])
        self.completed_missions = prog.get("completed_missions", [])

        compromised = prog.get("compromised_targets", [])
        for ip in compromised:
            if ip in self.available_targets:
                self.available_targets[ip]["compromised"] = True

    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.5)
            clear_screen()
            print()
            gradient_print("  ★ ═══════════════════════════════════════ ★", (255, 215, 0), (255, 140, 0))
            gradient_print(f"  ★         LEVEL UP! Now Level {self.level}!          ★", (255, 255, 0), (255, 165, 0))
            gradient_print(f"  ★         XP to next: {self.xp_to_next:<6}              ★", (255, 215, 0), (255, 140, 0))
            gradient_print("  ★ ═══════════════════════════════════════ ★", (255, 215, 0), (255, 140, 0))
            print()
            time.sleep(2)

    def increase_detection(self, amount):
        if self.vpn_active:
            amount = amount // 2
        amount = max(1, amount - self.proxy_chains * 5)
        self.detection_level = min(100, self.detection_level + amount)
        if 75 <= self.detection_level < 100:
            warning_flash("DETECTION LEVEL CRITICAL", 2)
        if self.detection_level >= 100:
            self.detected = True


# ============================================================
#                    MISSIONS SYSTEM
# ============================================================

class MissionSystem:
    def __init__(self):
        self.missions = [
            {"id": "m1", "title": "Script Kiddie's First Hack", "description": "Compromise the home router at 192.168.1.1",
             "target": "192.168.1.1", "objectives": ["Scan with nmap", "Crack password", "Exploit"],
             "reward_money": 200, "reward_xp": 50, "reward_rep": 5, "min_level": 1, "completed": False},
            {"id": "m2", "title": "Data Heist", "description": "Steal the customer database from 10.0.0.5",
             "target": "10.0.0.5", "objectives": ["Bypass firewall", "Crack password", "Download files"],
             "reward_money": 1000, "reward_xp": 150, "reward_rep": 15, "min_level": 2, "completed": False},
            {"id": "m3", "title": "Academic Espionage", "description": "Hack the university database",
             "target": "172.16.0.10", "objectives": ["Bypass firewall", "SQL inject", "Exfiltrate"],
             "reward_money": 2500, "reward_xp": 300, "reward_rep": 25, "min_level": 3, "completed": False},
            {"id": "m4", "title": "Dark Market Raid", "description": "Steal crypto from dark web market",
             "target": "198.51.100.20", "objectives": ["Bypass firewall", "Steal wallets"],
             "reward_money": 7500, "reward_xp": 400, "reward_rep": 35, "min_level": 3, "completed": False},
            {"id": "m5", "title": "Corporate Takedown", "description": "Steal MegaCorp trade secrets",
             "target": "10.10.10.1", "objectives": ["Bypass firewall", "Exploit SMB", "Install backdoor"],
             "reward_money": 5000, "reward_xp": 500, "reward_rep": 50, "min_level": 4, "completed": False},
            {"id": "m6", "title": "Shadow Government", "description": "Infiltrate classified server",
             "target": "10.20.30.40", "objectives": ["Chain proxies", "Bypass mil-grade firewall", "Decrypt files"],
             "reward_money": 15000, "reward_xp": 2000, "reward_rep": 100, "min_level": 5, "completed": False},
            {"id": "m7", "title": "The Big Score", "description": "Rob Bank of CyberCity",
             "target": "203.0.113.50", "objectives": ["Stealth approach", "Crack vault", "Clean logs"],
             "reward_money": 50000, "reward_xp": 5000, "reward_rep": 200, "min_level": 6, "completed": False},
            {"id": "m8", "title": "Orbital Strike", "description": "Hack satellite comm system",
             "target": "10.99.99.1", "objectives": ["Bypass RTOS security", "Access telemetry", "Download keys"],
             "reward_money": 75000, "reward_xp": 8000, "reward_rep": 500, "min_level": 7, "completed": False},
        ]

    def apply_save(self, mission_data):
        """Apply saved mission states."""
        saved = {m["id"]: m["completed"] for m in mission_data}
        for m in self.missions:
            if m["id"] in saved:
                m["completed"] = saved[m["id"]]


# ============================================================
#                     MAIN GAME
# ============================================================

class HackingSimulator:
    def __init__(self):
        self.state = GameState()
        self.missions = MissionSystem()
        self.command_history = []
        self.running = True
        self.auto_save_counter = 0
        ensure_game_dirs()

    # ========== PROFILE / SAVE MENU ==========

    def profile_menu(self):
        """Show profile selection menu at startup."""
        clear_screen()
        print()
        gradient_print("  ═══════════════════════════════════════════════", (0, 255, 255), (0, 100, 255))
        rainbow_text("         H A C K S T O R M   v 2 . 0")
        gradient_print("  ═══════════════════════════════════════════════", (0, 100, 255), (0, 255, 255))
        print()

        profiles = list_profiles()

        if profiles:
            p("  Saved Profiles:", C.LYELLOW + C.BOLD)
            print()
            for i, prof in enumerate(profiles, 1):
                p(f"    {C.LCYAN}{i}.{C.RESET} {C.BOLD}{prof['name']}{C.RESET} "
                  f"{C.DIM}(Lvl {prof['level']} | ${prof['money']:,} | "
                  f"Missions {prof['missions']}/{prof['total_missions']} | "
                  f"Last: {prof['timestamp']}){C.RESET}")
            print()

        p(f"  {C.LGREEN}N{C.RESET} - New Profile", C.LWHITE)
        if profiles:
            p(f"  {C.LYELLOW}L{C.RESET} - Load Profile", C.LWHITE)
            p(f"  {C.LRED}D{C.RESET} - Delete Profile", C.LWHITE)
        p(f"  {C.LRED}Q{C.RESET} - Quit", C.LWHITE)
        print()

        choice = input(f"  {C.LCYAN}>{C.RESET} ").strip().lower()

        if choice == 'n':
            return self._new_profile()
        elif choice == 'l' and profiles:
            return self._load_profile(profiles)
        elif choice == 'd' and profiles:
            self._delete_profile(profiles)
            return self.profile_menu()
        elif choice == 'q':
            p("\n  Goodbye.\n", C.LCYAN)
            sys.exit(0)
        else:
            return self.profile_menu()

    def _new_profile(self):
        print()
        name = input(f"  {C.LGREEN}Enter hacker alias:{C.RESET} ").strip()
        if not name:
            name = "ghost"
        self.state.player_name = name

        # Check if profile already exists
        existing = load_game(name)
        if existing:
            p(f"  Profile '{name}' already exists!", C.LYELLOW)
            overwrite = input(f"  Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                return self.profile_menu()

        return "new"

    def _load_profile(self, profiles):
        print()
        try:
            idx = int(input(f"  {C.LYELLOW}Enter profile number:{C.RESET} ").strip()) - 1
            if 0 <= idx < len(profiles):
                prof = profiles[idx]
                data = load_game(prof["name"])
                if data:
                    self.state = GameState()
                    self.state.apply_save(data)
                    self.missions = MissionSystem()
                    self.missions.apply_save(data.get("missions", []))
                    p(f"\n  {C.LGREEN}Profile '{prof['name']}' loaded!{C.RESET}")
                    time.sleep(1)
                    return "loaded"
                else:
                    p("  Failed to load profile.", C.LRED)
            else:
                p("  Invalid selection.", C.LRED)
        except ValueError:
            p("  Invalid input.", C.LRED)
        return self.profile_menu()

    def _delete_profile(self, profiles):
        print()
        try:
            idx = int(input(f"  {C.LRED}Delete profile number:{C.RESET} ").strip()) - 1
            if 0 <= idx < len(profiles):
                prof = profiles[idx]
                confirm = input(f"  Delete '{prof['name']}'? Type 'yes': ").strip().lower()
                if confirm == 'yes':
                    delete_profile(prof["name"])
                    p(f"  Profile '{prof['name']}' deleted.", C.LRED)
                else:
                    p("  Cancelled.", C.LYELLOW)
            else:
                p("  Invalid selection.", C.LRED)
        except ValueError:
            p("  Invalid input.", C.LRED)
        time.sleep(1)

    # ========== TUTORIAL ==========

    def show_tutorial(self):
        pages = [
            {
                "title": "THE BASICS",
                "content": [
                    f"  {C.LWHITE}You are a hacker operating from your terminal.{C.RESET}",
                    f"  {C.LWHITE}Your goal: complete missions, earn money, level up.{C.RESET}",
                    "",
                    f"  {C.LYELLOW}Key commands:{C.RESET}",
                    f"    {C.LGREEN}help{C.RESET}      - See all commands",
                    f"    {C.LGREEN}status{C.RESET}    - Check your stats",
                    f"    {C.LGREEN}missions{C.RESET}  - See available jobs",
                    f"    {C.LGREEN}targets{C.RESET}   - See hackable systems",
                    f"    {C.LGREEN}shop{C.RESET}      - Buy tools and upgrades",
                    f"    {C.LGREEN}save{C.RESET}      - Save your progress",
                ],
            },
            {
                "title": "HOW TO HACK",
                "content": [
                    f"  {C.LWHITE}Every hack follows these steps:{C.RESET}",
                    "",
                    f"  {C.LCYAN}1.{C.RESET} {C.LGREEN}nmap <ip>{C.RESET}            - Scan for open ports",
                    f"  {C.LCYAN}2.{C.RESET} {C.LGREEN}firewall_bypass <ip>{C.RESET}  - Bypass firewall (if any)",
                    f"  {C.LCYAN}3.{C.RESET} {C.LGREEN}crack <ip>{C.RESET}            - Crack the password",
                    f"  {C.LCYAN}4.{C.RESET} {C.LGREEN}exploit <ip>{C.RESET}          - Take over the system",
                    f"  {C.LCYAN}5.{C.RESET} {C.LGREEN}connect <ip>{C.RESET}          - Access the system",
                    f"  {C.LCYAN}6.{C.RESET} {C.LGREEN}download <file>{C.RESET}       - Steal files",
                    f"  {C.LCYAN}7.{C.RESET} {C.LGREEN}clean_logs <ip>{C.RESET}       - Hide your tracks",
                ],
            },
            {
                "title": "STAY HIDDEN",
                "content": [
                    f"  {C.LRED}Every action increases your DETECTION level!{C.RESET}",
                    "",
                    f"  {C.LWHITE}Detection Bar:{C.RESET}",
                    f"  {C.LGREEN}[██████████{C.STEEL}░░░░░░░░░░{C.RESET}] 50% {C.LYELLOW}<- Getting risky!{C.RESET}",
                    "",
                    f"  {C.LRED}If detection reaches 100%... GAME OVER!{C.RESET}",
                    "",
                    f"  {C.LYELLOW}How to stay safe:{C.RESET}",
                    f"    {C.LGREEN}buy vpn{C.RESET}         - Reduces detection gain by 50%",
                    f"    {C.LGREEN}buy proxy_chain{C.RESET} - Each reduces detection by 5",
                    f"    {C.LGREEN}clean_logs <ip>{C.RESET} - Reduces detection by 30%",
                ],
            },
            {
                "title": "TOOLS & MONEY",
                "content": [
                    f"  {C.LWHITE}You start with $1,000 and basic tools.{C.RESET}",
                    "",
                    f"  {C.LYELLOW}Essential first purchases:{C.RESET}",
                    f"    {C.ORANGE}hydra{C.RESET}      ${C.GOLD}300{C.RESET}  - Crack passwords",
                    f"    {C.ORANGE}metasploit{C.RESET} ${C.GOLD}800{C.RESET}  - Exploit targets",
                    f"    {C.ORANGE}vpn{C.RESET}        ${C.GOLD}200{C.RESET}  - Stay hidden",
                    "",
                    f"  {C.LWHITE}Earn money from missions and hacking!{C.RESET}",
                    f"  {C.LWHITE}Your progress auto-saves every 5 commands.{C.RESET}",
                ],
            },
            {
                "title": "YOUR FIRST MISSION",
                "content": [
                    f"  {C.LWHITE}Target: 192.168.1.1 (Home Router){C.RESET}",
                    f"  {C.LWHITE}Difficulty: * (Easy) | No firewall!{C.RESET}",
                    "",
                    f"  {C.LYELLOW}Steps:{C.RESET}",
                    f"    {C.LCYAN}1.{C.RESET} {C.LGREEN}buy hydra{C.RESET}",
                    f"    {C.LCYAN}2.{C.RESET} {C.LGREEN}nmap 192.168.1.1{C.RESET}",
                    f"    {C.LCYAN}3.{C.RESET} {C.LGREEN}crack 192.168.1.1{C.RESET}",
                    f"    {C.LCYAN}4.{C.RESET} {C.LGREEN}buy metasploit{C.RESET}",
                    f"    {C.LCYAN}5.{C.RESET} {C.LGREEN}exploit 192.168.1.1{C.RESET}",
                    f"    {C.LCYAN}6.{C.RESET} {C.LGREEN}connect 192.168.1.1{C.RESET}",
                    f"    {C.LCYAN}7.{C.RESET} {C.LGREEN}download router_config.txt{C.RESET}",
                    "",
                    f"  {C.BOLD}{C.NEON_GREEN}You're ready to hack!{C.RESET}",
                ],
            },
        ]

        for i, page in enumerate(pages):
            clear_screen()
            print()
            gradient_print(f"  ═══ TUTORIAL ({i+1}/{len(pages)}) ═══════════════════════════", (0, 255, 255), (100, 150, 255))
            neon_box(page["title"], C.LCYAN)
            print()
            for line in page["content"]:
                print(line)
                time.sleep(0.05)
            print()
            if i < len(pages) - 1:
                input(f"  {C.DIM}[Press ENTER to continue]{C.RESET}")
            else:
                input(f"  {C.LGREEN}[Press ENTER to start hacking!]{C.RESET}")

        self.state.tutorial_done = True
        clear_screen()
        self.show_banner()

    # ========== BOOT & LOGIN ==========

    def boot_sequence(self):
        clear_screen()
        matrix_rain(2)
        clear_screen()

        gradient_print("  ═══════════════════════════════════════════════════", (0, 255, 255), (0, 100, 255))
        gradient_print("          CYBER-OS v4.2.0 BOOT SEQUENCE", (0, 200, 255), (100, 255, 200))
        gradient_print("  ═══════════════════════════════════════════════════", (0, 100, 255), (0, 255, 255))
        print()

        boot_msgs = [
            "Loading BIOS firmware",
            "CPU: Quantum i9-X @ 6.66 GHz",
            "RAM: 16384 MB DDR5 validated",
            "GPU: Shadow RTX 9090",
            "Storage: 2TB NVMe SSD mounted",
            "Network adapter initialized",
            "Loading kernel cyberOS-6.6.6",
            "Mounting filesystems",
            "Starting network daemon",
            "Configuring DNS",
            "Loading crypto module (AES-256)",
            "Starting hacking framework v4.2",
        ]

        for msg in boot_msgs:
            type_loading(msg, random.uniform(0.2, 0.6))

        print()
        p(f"  {C.BOLD}{C.LGREEN}[SYSTEM] All systems operational.{C.RESET}")
        time.sleep(1)
        clear_screen()

    def login_screen(self):
        clear_screen()
        print()
        gradient_print("  ╔══════════════════════════════════════════════╗", (0, 255, 255), (100, 100, 255))
        gradient_print("  ║         CYBER-OS SECURE LOGIN               ║", (0, 200, 255), (150, 100, 255))
        gradient_print("  ╚══════════════════════════════════════════════╝", (100, 100, 255), (0, 255, 255))
        print()
        p(f"  Logging in as: {C.BOLD}{C.LCYAN}{self.state.player_name}{C.RESET}")
        print()

        getpass.getpass(f"  {C.LGREEN}Enter password:{C.RESET} ")

        print()
        type_loading("Authenticating", 1)
        type_loading("Verifying identity", 0.6)
        type_loading("Loading profile", 0.6)
        type_loading("Establishing encrypted session", 0.4)

        print()
        decrypt_animation(f"Welcome back, {self.state.player_name}.")
        p(f"  {C.DIM}IP: {self.state.ip_address} | Session: AES-256{C.RESET}")
        p(f"  {C.DIM}Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}")
        p(f"  {C.DIM}Save dir: {get_user_dir(self.state.player_name)}{C.RESET}")
        time.sleep(2)
        clear_screen()

    def show_banner(self):
        print()
        gradient_print("    ╦ ╦╔═╗╔═╗╦╔═╔═╗╔╦╗╔═╗╦═╗╔╦╗", (0, 255, 100), (0, 200, 255))
        gradient_print("    ╠═╣╠═╣║  ╠╩╗╚═╗ ║ ║ ║╠╦╝║║║", (0, 200, 255), (100, 100, 255))
        gradient_print("    ╩ ╩╩ ╩╚═╝╩ ╩╚═╝ ╩ ╚═╝╩╚═╩ ╩", (100, 100, 255), (200, 0, 255))
        print()
        gradient_print("  ═══════════════════════════════════════════", (50, 50, 50), (150, 150, 150))
        p(f"   {C.BOLD}{C.LWHITE}Terminal Hacking Simulator v2.0{C.RESET}")
        p(f"   {C.DIM}Type 'help' for commands | 'tutorial' to learn{C.RESET}")
        p(f"   {C.DIM}Progress saves to: {GAME_DIR}{C.RESET}")
        gradient_print("  ═══════════════════════════════════════════", (150, 150, 150), (50, 50, 50))
        print()

    def get_prompt(self):
        net = self.state.current_network
        parts = []
        if self.state.vpn_active:
            parts.append(f"{C.LGREEN}[VPN]{C.RESET}")
        if self.state.detection_level > 0:
            if self.state.detection_level < 30:
                det_color = C.LGREEN
            elif self.state.detection_level < 70:
                det_color = C.LYELLOW
            else:
                det_color = C.LRED
            parts.append(f"{det_color}[DET:{self.state.detection_level}%]{C.RESET}")

        extra = " ".join(parts)
        if extra:
            extra = " " + extra
        return f"{C.LRED}{self.state.player_name}{C.RESET}@{C.LCYAN}{net}{C.RESET}{extra} {C.LGREEN}${C.RESET} "

    # ========== COMMANDS ==========

    def cmd_help(self, args):
        clear_screen()
        commands = {
            "GENERAL": {
                "help": "Show this menu",
                "status": "Your stats",
                "clear": "Clear terminal",
                "missions": "Mission board",
                "shop": "Black market",
                "buy <item>": "Purchase item",
                "inventory": "Your stuff",
                "targets": "Hackable systems",
                "tutorial": "Replay tutorial",
                "save": "Save progress",
                "whoami": "Identity info",
                "time": "System time",
                "history": "Command log",
                "note <text>": "Save a note",
                "notes": "View notes",
                "crypto": "Crypto wallet",
                "leaderboard": "Rankings",
                "exit": "Exit game",
            },
            "NETWORK": {
                "nmap <ip>": "Port scan",
                "ping <ip>": "Check host",
                "connect <ip>": "Connect to target",
                "disconnect": "Disconnect",
                "traceroute <ip>": "Trace route",
                "netmap": "Network map",
                "whois <ip>": "Target lookup",
                "dns <domain>": "DNS lookup",
            },
            "HACKING": {
                "crack <ip>": "Crack password",
                "exploit <ip>": "Run exploit",
                "sqlinject <ip>": "SQL injection",
                "sniff": "Sniff traffic",
                "bruteforce <ip>": "Brute-force",
                "firewall_bypass <ip>": "Bypass firewall",
                "phish <ip>": "Phishing attack",
                "ddos <ip>": "DDoS attack",
                "wifihack": "Hack WiFi",
            },
            "POST-EXPLOIT": {
                "download <file>": "Download file",
                "backdoor <ip>": "Install backdoor",
                "clean_logs <ip>": "Clean traces",
                "cat <file>": "Read file",
                "mine <ip>": "Mine crypto",
                "analyze <file>": "Forensic analysis",
            },
            "DEFENSE": {
                "vpn": "Toggle VPN",
                "proxy": "Proxy status",
                "encrypt <file>": "Encrypt file",
                "shred <file>": "Delete file",
                "spoof": "Spoof MAC",
            },
        }

        print()
        gradient_print("  ═══ COMMAND REFERENCE ═══════════════════════════", (0, 255, 255), (100, 100, 255))
        print()

        category_colors = {
            "GENERAL": C.LGREEN,
            "NETWORK": C.LCYAN,
            "HACKING": C.LRED,
            "POST-EXPLOIT": C.ORANGE,
            "DEFENSE": C.LBLUE,
        }

        for category, cmds in commands.items():
            cat_color = category_colors.get(category, C.LYELLOW)
            print()
            p(f"  {cat_color}{C.BOLD}━━ {category} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}")
            for cmd, desc in cmds.items():
                p(f"    {C.LWHITE}{cmd:<25}{C.RESET}{C.DIM}{desc}{C.RESET}")
        print()

    def cmd_save(self, args):
        success = save_game(self.state, self.missions, self.state.player_name)
        if success:
            p(f"  {C.LGREEN}[OK] Game saved to {get_user_dir(self.state.player_name)}{C.RESET}")
        else:
            p(f"  {C.LRED}[ERROR] Failed to save game.{C.RESET}")

    def auto_save(self):
        self.auto_save_counter += 1
        if self.auto_save_counter % 5 == 0:
            save_game(self.state, self.missions, self.state.player_name)

    def cmd_status(self, args):
        clear_screen()
        s = self.state
        print()
        gradient_print("  ═══ HACKER PROFILE ═══════════════════════════════", (0, 255, 200), (0, 150, 255))
        print()
        p(f"    {C.STEEL}Alias:{C.RESET}       {C.BOLD}{C.LCYAN}{s.player_name}{C.RESET}")
        p(f"    {C.STEEL}IP Address:{C.RESET}  {C.LGREEN}{s.ip_address}{C.RESET}")
        p(f"    {C.STEEL}Level:{C.RESET}       {C.GOLD}{C.BOLD}{s.level}{C.RESET}")

        xp_pct = s.xp / s.xp_to_next if s.xp_to_next > 0 else 0
        bar_len = 20
        filled = int(xp_pct * bar_len)
        try:
            xp_bar = f"{C.LCYAN}{'█' * filled}{C.STEEL}{'░' * (bar_len - filled)}{C.RESET}"
        except UnicodeEncodeError:
            xp_bar = f"{'#' * filled}{'-' * (bar_len - filled)}"
        p(f"    {C.STEEL}XP:{C.RESET}          [{xp_bar}] {C.LWHITE}{s.xp}/{s.xp_to_next}{C.RESET}")

        p(f"    {C.STEEL}Money:{C.RESET}       {C.GOLD}${s.money:,}{C.RESET}")
        p(f"    {C.STEEL}Crypto:{C.RESET}      {C.ORANGE}{s.crypto_wallet:.6f} BTC{C.RESET}")
        p(f"    {C.STEEL}Reputation:{C.RESET}  {C.LMAGENTA}{s.reputation} pts{C.RESET}")

        vpn_color = C.LGREEN if s.vpn_active else C.LRED
        vpn_text = "ACTIVE" if s.vpn_active else "INACTIVE"
        p(f"    {C.STEEL}VPN:{C.RESET}         {vpn_color}{vpn_text}{C.RESET}")
        p(f"    {C.STEEL}Proxies:{C.RESET}     {C.LBLUE}{s.proxy_chains} chains{C.RESET}")
        p(f"    {C.STEEL}Botnet:{C.RESET}      {C.PURPLE}{s.botnet_size} nodes{C.RESET}")

        det = s.detection_level
        det_filled = int((det / 100) * 20)
        if det < 30:
            det_color = C.LGREEN
            det_label = "LOW"
        elif det < 70:
            det_color = C.LYELLOW
            det_label = "MEDIUM"
        else:
            det_color = C.LRED
            det_label = "CRITICAL!"
        try:
            det_bar = f"{det_color}{'█' * det_filled}{C.STEEL}{'░' * (20 - det_filled)}{C.RESET}"
        except UnicodeEncodeError:
            det_bar = f"{'#' * det_filled}{'-' * (20 - det_filled)}"
        p(f"    {C.STEEL}Detection:{C.RESET}   [{det_bar}] {det_color}{det}% ({det_label}){C.RESET}")

        p(f"    {C.STEEL}Network:{C.RESET}     {C.LCYAN}{s.current_network}{C.RESET}")
        if s.connected_to:
            p(f"    {C.STEEL}Connected:{C.RESET}   {C.LGREEN}{s.connected_to}{C.RESET}")

        completed = len([m for m in self.missions.missions if m['completed']])
        total = len(self.missions.missions)
        p(f"    {C.STEEL}Missions:{C.RESET}    {C.LWHITE}{completed}/{total}{C.RESET}")
        p(f"    {C.STEEL}Backdoors:{C.RESET}   {C.LRED}{len(s.backdoors)}{C.RESET}")
        p(f"    {C.STEEL}Passwords:{C.RESET}   {C.LGREEN}{len(s.known_passwords)} cracked{C.RESET}")
        p(f"    {C.STEEL}Save Dir:{C.RESET}    {C.DIM}{get_user_dir(s.player_name)}{C.RESET}")
        print()

    def cmd_targets(self, args):
        clear_screen()
        print()
        gradient_print("  ═══ KNOWN TARGETS ════════════════════════════════", (255, 100, 100), (255, 50, 50))
        print()
        for ip, info in self.state.available_targets.items():
            if info["compromised"]:
                status = f"{C.LGREEN}[COMPROMISED]{C.RESET}"
                ip_color = C.LGREEN
            else:
                status = f"{C.LRED}[SECURED]{C.RESET}"
                ip_color = C.LRED

            try:
                diff = f"{C.GOLD}{'★' * info['difficulty']}{'☆' * (5 - info['difficulty'])}{C.RESET}"
            except UnicodeEncodeError:
                diff = f"{'*' * info['difficulty']}{'.' * (5 - info['difficulty'])}"

            p(f"    {C.BOLD}{ip_color}{ip:<18}{C.RESET} {C.LWHITE}{info['name']}{C.RESET}")
            p(f"      {C.STEEL}OS:{C.RESET} {info['os']}  {C.STEEL}|{C.RESET}  {diff}  {C.STEEL}|{C.RESET}  {status}")
            fw = f"{C.LYELLOW}Yes (Lvl {info.get('firewall_level', 0)}){C.RESET}" if info['firewall'] else f"{C.LGREEN}No{C.RESET}"
            p(f"      {C.STEEL}Firewall:{C.RESET} {fw}")
            print()

    def cmd_nmap(self, args):
        if "nmap" not in self.state.tools:
            p("  [ERROR] nmap not installed.", C.LRED)
            return
        if not args:
            p("  [USAGE] nmap <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        if target_ip not in self.state.available_targets:
            p(f"  [ERROR] Host {target_ip} not found.", C.LRED)
            return

        clear_screen()
        target = self.state.available_targets[target_ip]
        self.state.increase_detection(5)
        print()
        glitch_text(f"  NMAP SCAN - Target: {target_ip}")
        print()
        scan_animation(target_ip, 3)
        print()
        p(f"  {C.BOLD}{C.LWHITE}Nmap scan report for {target_ip}{C.RESET}")
        p(f"  {C.DIM}Host is up (0.{random.randint(1,99):02d}ms latency){C.RESET}")
        p(f"  {C.DIM}OS: {target['os']}{C.RESET}")
        print()
        p(f"  {C.BOLD}{C.LWHITE}{'PORT':<12}{'STATE':<10}{'SERVICE':<15}{C.RESET}")
        gradient_print(f"  {'─' * 37}", (100, 100, 100), (50, 50, 50))

        for port, service in target['ports'].items():
            time.sleep(0.3)
            p(f"  {C.LCYAN}{str(port) + '/tcp':<12}{C.LGREEN}{'open':<10}{C.LWHITE}{service:<15}{C.RESET}")

        print()
        if target['firewall']:
            p(f"  {C.BG_DARK_RED}{C.LYELLOW}{C.BOLD} FIREWALL DETECTED (Level {target.get('firewall_level', 1)}) {C.RESET}")
        else:
            p(f"  {C.LGREEN}[OK] No firewall detected{C.RESET}")
        print()

    def cmd_ping(self, args):
        if not args:
            p("  [USAGE] ping <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        print()
        for i in range(4):
            ms = random.uniform(0.5, 50.0)
            if target_ip in self.state.available_targets:
                p(f"  {C.LGREEN}Reply from {target_ip}: bytes=64 time={ms:.1f}ms TTL={random.randint(50,128)}{C.RESET}")
            else:
                p(f"  {C.LRED}Request timed out.{C.RESET}")
            time.sleep(0.5)
        print()

    def cmd_traceroute(self, args):
        if not args:
            p("  [USAGE] traceroute <ip>", C.LYELLOW)
            return
        clear_screen()
        target_ip = args[0]
        print()
        glitch_text(f"  TRACEROUTE - {target_ip}")
        print()
        hops = random.randint(5, 15)
        for i in range(1, hops + 1):
            ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            ms1 = random.uniform(1, 100)
            p(f"  {C.LCYAN}{i:>3}{C.RESET}   {ms1:>7.2f} ms  {ip}")
            time.sleep(0.2)
        p(f"  {C.LGREEN}{hops+1:>3}{C.RESET}   {'*':>7}      {target_ip}")
        print()

    def cmd_connect(self, args):
        if not args:
            p("  [USAGE] connect <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        if target_ip not in self.state.available_targets:
            p(f"  [ERROR] Cannot resolve {target_ip}.", C.LRED)
            return
        target = self.state.available_targets[target_ip]
        if not target["compromised"]:
            p(f"\n  {C.BG_DARK_RED}{C.LWHITE}{C.BOLD} ACCESS DENIED {C.RESET}")
            p("  [HINT] Hack it first: nmap > crack > exploit", C.LYELLOW)
            return
        type_loading(f"Connecting to {target_ip}", 1.5)
        self.state.connected_to = target_ip
        self.state.current_network = target["name"].replace(" ", "_").lower()
        p(f"\n  {C.BG_DARK_GREEN}{C.LWHITE}{C.BOLD} ACCESS GRANTED {C.RESET}")
        p(f"  {C.LGREEN}Connected: {target['name']} | OS: {target['os']}{C.RESET}")

    def cmd_disconnect(self, args):
        if not self.state.connected_to:
            p("  [INFO] Not connected.", C.LYELLOW)
            return
        p(f"  {C.LGREEN}Disconnected from {self.state.connected_to}{C.RESET}")
        self.state.connected_to = None
        self.state.current_network = "home"

    def cmd_crack(self, args):
        if "hydra" not in self.state.tools and "john" not in self.state.tools:
            p("  [ERROR] No cracking tool. Buy 'hydra' or 'john'.", C.LRED)
            return
        if not args:
            p("  [USAGE] crack <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        if target_ip not in self.state.available_targets:
            p(f"  [ERROR] Unknown target {target_ip}", C.LRED)
            return
        target = self.state.available_targets[target_ip]
        if target["firewall"] and not self.state.firewall_bypassed:
            p("  [ERROR] Firewall blocking! Use 'firewall_bypass' first.", C.LRED)
            self.state.increase_detection(15)
            return

        clear_screen()
        self.state.increase_detection(10)
        print()
        glitch_text(f"  PASSWORD CRACKER - {target_ip}")
        print()
        tool = "Hydra" if "hydra" in self.state.tools else "John"
        p(f"  {C.LCYAN}Tool: {tool} | Wordlist: rockyou.txt{C.RESET}")
        print()
        hacker_progress_bar("Cracking hash...", random.uniform(2, 4))
        fake_data_stream(5)

        difficulty = target["difficulty"]
        success = max(20, 90 - (difficulty * 15) + (self.state.level * 10))
        if "john" in self.state.tools and "hydra" in self.state.tools:
            success += 15

        if random.randint(1, 100) <= success:
            password = target["password"]
            self.state.known_passwords[target_ip] = password
            print()
            password_crack_animation(password, 2)
            print()
            neon_box(f"PASSWORD CRACKED: {password}", C.LGREEN)
        else:
            print()
            p(f"  {C.LRED}[FAIL] Crack failed. Level up or get better tools.{C.RESET}")
        print()

    def cmd_firewall_bypass(self, args):
        if not args:
            p("  [USAGE] firewall_bypass <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        if target_ip not in self.state.available_targets:
            p(f"  [ERROR] Unknown target.", C.LRED)
            return
        target = self.state.available_targets[target_ip]
        if not target["firewall"]:
            p("  [INFO] No firewall on this target.", C.LYELLOW)
            return

        clear_screen()
        fw_level = target.get("firewall_level", 1)
        self.state.increase_detection(10 + fw_level * 5)
        print()
        glitch_text(f"  FIREWALL BYPASS - {target_ip}")
        print()
        p(f"  {C.LRED}{'█' * 40}{C.RESET}")
        p(f"  {C.LRED}█{C.RESET} {C.BOLD}{C.LWHITE}F I R E W A L L  (Level {fw_level}){C.RESET}        {C.LRED}█{C.RESET}")
        p(f"  {C.LRED}{'█' * 40}{C.RESET}")
        print()
        type_loading("Probing firewall rules", 1.5)
        type_loading("Searching vulnerabilities", 2)

        if "zero_day" in self.state.tools:
            p(f"\n  {C.NEON_PINK}{C.BOLD}Deploying ZERO-DAY exploit...{C.RESET}")
            hacker_progress_bar("Bypassing...", 1.5)
            p(f"  {C.BG_DARK_GREEN}{C.LWHITE}{C.BOLD} FIREWALL BYPASSED (zero-day) {C.RESET}")
            self.state.firewall_bypassed = True
            return

        success = max(10, 80 - (fw_level * 15) + (self.state.level * 8))
        if "metasploit" in self.state.tools:
            success += 20
        hacker_progress_bar("Attempting bypass...", 3)

        if random.randint(1, 100) <= success:
            self.state.firewall_bypassed = True
            p(f"\n  {C.BG_DARK_GREEN}{C.LWHITE}{C.BOLD} FIREWALL BYPASSED! {C.RESET}")
        else:
            p(f"\n  {C.LRED}[FAIL] Too strong. Get 'metasploit' or 'zero_day'.{C.RESET}")
            self.state.increase_detection(10)
        print()

    def cmd_exploit(self, args):
        if "metasploit" not in self.state.tools:
            p("  [ERROR] Need metasploit. Buy from shop.", C.LRED)
            return
        if not args:
            p("  [USAGE] exploit <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        if target_ip not in self.state.available_targets:
            p(f"  [ERROR] Unknown target.", C.LRED)
            return
        target = self.state.available_targets[target_ip]
        if target["compromised"]:
            p("  [INFO] Already compromised.", C.LYELLOW)
            return
        if target_ip not in self.state.known_passwords:
            p("  [ERROR] Crack password first.", C.LRED)
            return
        if target["firewall"] and not self.state.firewall_bypassed:
            p("  [ERROR] Firewall active! Bypass first.", C.LRED)
            return

        clear_screen()
        self.state.increase_detection(15)
        print()
        glitch_text(f"  EXPLOIT LAUNCHER - {target_ip}")
        print()

        exploits = ["ms17_010_eternalblue", "vsftpd_234_backdoor", "libssh_auth_bypass", "apache_struts_rce"]
        selected = random.choice(exploits)
        p(f"  {C.LCYAN}Exploit:{C.RESET}  {selected}")
        p(f"  {C.LCYAN}Payload:{C.RESET}  meterpreter/reverse_tcp")
        p(f"  {C.LCYAN}LHOST:{C.RESET}    {self.state.ip_address}")
        p(f"  {C.LCYAN}LPORT:{C.RESET}    4444")
        print()
        type_loading("Sending exploit", 1.5)
        hacker_progress_bar("Executing payload...", 2)
        fake_data_stream(8)

        difficulty = target["difficulty"]
        success = max(30, 85 - (difficulty * 10) + (self.state.level * 10))

        if random.randint(1, 100) <= success:
            target["compromised"] = True
            self.state.firewall_bypassed = False
            print()
            p(f"  {C.BG_DARK_GREEN}{C.LWHITE}{C.BOLD} ★ SYSTEM COMPROMISED! ★ {C.RESET}")
            p(f"  {C.LGREEN}Target: {target['name']} | Access: ROOT{C.RESET}")
            print()

            loot = target["loot"]
            self.state.money += loot["money"]
            self.state.add_xp(loot["xp"])
            for f in loot["files"]:
                if f not in self.state.files:
                    self.state.files.append(f)

            p(f"  {C.GOLD}+${loot['money']:,}{C.RESET}  {C.LCYAN}+{loot['xp']} XP{C.RESET}")
            p(f"  {C.LGREEN}Files: {', '.join(loot['files'])}{C.RESET}")
            self._check_missions(target_ip)
        else:
            print()
            p(f"  {C.BG_DARK_RED}{C.LWHITE}{C.BOLD} EXPLOIT FAILED {C.RESET}")
            self.state.increase_detection(20)
        print()

    def cmd_sqlinject(self, args):
        if "sqlmap" not in self.state.tools:
            p("  [ERROR] sqlmap not installed.", C.LRED)
            return
        if not args:
            p("  [USAGE] sqlinject <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        if target_ip not in self.state.available_targets:
            p(f"  [ERROR] Unknown target.", C.LRED)
            return
        target = self.state.available_targets[target_ip]
        has_db = any(s in ["MySQL", "PostgreSQL", "MSSQL"] for s in target.get("services", []))
        if not has_db:
            p("  [ERROR] No database service on target.", C.LRED)
            return

        clear_screen()
        self.state.increase_detection(10)
        print()
        glitch_text(f"  SQL INJECTION - {target_ip}")
        print()
        payloads = ["' OR 1=1 --", "' UNION SELECT * FROM users --", "'; DROP TABLE users; --"]
        for pl in payloads:
            typing_animation(pl, 0.02)
            time.sleep(0.2)
        hacker_progress_bar("Exploiting injection...", 2)

        if random.randint(1, 100) <= 70 + self.state.level * 5:
            print()
            p(f"  {C.BG_DARK_GREEN}{C.LWHITE}{C.BOLD} SQL INJECTION SUCCESSFUL {C.RESET}")
            print()
            tables = ["users", "accounts", "transactions", "config"]
            p(f"  {C.BOLD}{C.LWHITE}{'TABLE':<20}{'ROWS':<10}{'COLS'}{C.RESET}")
            for t in tables:
                p(f"  {C.LGREEN}{t:<20}{random.randint(100,50000):<10}{random.randint(3,15)}{C.RESET}")
                time.sleep(0.2)
            self.state.add_xp(50)
            self.state.money += 200
        else:
            p(f"  {C.LRED}[FAIL] No injectable parameters.{C.RESET}")
        print()

    def cmd_sniff(self, args):
        if "wireshark" not in self.state.tools:
            p("  [ERROR] Wireshark not installed.", C.LRED)
            return
        clear_screen()
        print()
        glitch_text("  PACKET SNIFFER - Capturing traffic")
        print()
        protocols = ["TCP", "UDP", "HTTP", "HTTPS", "DNS", "FTP", "SSH"]
        proto_colors = {"TCP": C.LCYAN, "UDP": C.LBLUE, "HTTP": C.LGREEN, "HTTPS": C.LIME,
                        "DNS": C.LYELLOW, "FTP": C.ORANGE, "SSH": C.LMAGENTA}
        for i in range(20):
            src = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            dst = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            proto = random.choice(protocols)
            size = random.randint(40, 1500)
            port = random.choice([21, 22, 53, 80, 443, 3306])
            pc = proto_colors.get(proto, C.LWHITE)
            p(f"  {C.DIM}{i+1:>4}{C.RESET}  {src}:{random.randint(1024,65535)} {C.STEEL}->{C.RESET} {dst}:{port}  {pc}{proto:<6}{C.RESET} {size}B")
            time.sleep(0.12)
            if random.randint(1, 15) == 1:
                u = random.choice(["admin", "root", "user"])
                pw = random.choice(["letmein123", "pass123", "qwerty"])
                p(f"        {C.BG_DARK_RED}{C.LWHITE} INTERCEPTED: {u}:{pw} {C.RESET}")
                self.state.intercepted_data.append(f"{u}:{pw}")
        print()
        p(f"  {C.LGREEN}Capture complete. {len(self.state.intercepted_data)} credentials intercepted.{C.RESET}")
        self.state.add_xp(25)
        print()

    def cmd_bruteforce(self, args):
        if "hydra" not in self.state.tools:
            p("  [ERROR] Hydra not installed.", C.LRED)
            return
        if not args:
            p("  [USAGE] bruteforce <ip>", C.LYELLOW)
            return
        clear_screen()
        self.state.increase_detection(20)
        print()
        glitch_text(f"  BRUTE FORCE - {args[0]}")
        p(f"  {C.BG_DARK_RED}{C.LWHITE} WARNING: HIGH DETECTION RISK {C.RESET}")
        print()
        attempts = random.randint(500, 5000)
        for i in range(0, attempts, attempts // 20):
            pwd = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=random.randint(6, 12)))
            sys.stdout.write(f"\r  {C.LYELLOW}[{i}/{attempts}]{C.RESET} Trying: {C.DIM}{pwd}{C.RESET}          ")
            sys.stdout.flush()
            time.sleep(0.08)

        target_ip = args[0]
        if target_ip in self.state.available_targets:
            target = self.state.available_targets[target_ip]
            password = target["password"]
            print("\n")
            password_crack_animation(password, 2)
            neon_box(f"Password: {password}", C.LGREEN)
            self.state.known_passwords[target_ip] = password
        else:
            print(f"\n\n  {C.LRED}[FAIL] Brute force failed.{C.RESET}")
        print()

    def cmd_download(self, args):
        if not self.state.connected_to:
            p("  [ERROR] Not connected. Use 'connect <ip>'.", C.LRED)
            return
        if not args:
            p("  [USAGE] download <file>", C.LYELLOW)
            return
        filename = args[0]
        target = self.state.available_targets[self.state.connected_to]
        available = target["loot"]["files"]
        if filename not in available:
            p(f"  [ERROR] '{filename}' not found. Available: {', '.join(available)}", C.LRED)
            return
        print()
        hacker_progress_bar(f"Downloading {filename}...", random.uniform(1.5, 4))
        if filename not in self.state.files:
            self.state.files.append(filename)
        p(f"  {C.LGREEN}Downloaded {filename}{C.RESET}")
        self.state.increase_detection(5)
        self.state.add_xp(20)
        print()

    def cmd_backdoor(self, args):
        if "rootkit" not in self.state.tools:
            p("  [ERROR] Rootkit not installed.", C.LRED)
            return
        if not args:
            p("  [USAGE] backdoor <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        if target_ip not in self.state.available_targets or not self.state.available_targets[target_ip]["compromised"]:
            p("  [ERROR] Target not compromised.", C.LRED)
            return
        print()
        type_loading("Deploying rootkit", 2)
        type_loading("Hiding processes", 1)
        self.state.backdoors.append(target_ip)
        p(f"  {C.LGREEN}Backdoor installed on {target_ip} (port 31337){C.RESET}")
        self.state.add_xp(40)
        print()

    def cmd_clean_logs(self, args):
        if not args:
            p("  [USAGE] clean_logs <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        if target_ip not in self.state.available_targets or not self.state.available_targets[target_ip]["compromised"]:
            p("  [ERROR] No access.", C.LRED)
            return
        clear_screen()
        print()
        glitch_text(f"  LOG CLEANER - {target_ip}")
        print()
        logs = ["/var/log/auth.log", "/var/log/syslog", "/var/log/access.log", "/var/log/secure"]
        for log in logs:
            type_loading(f"Wiping {log}", random.uniform(0.2, 0.5))
        self.state.log_cleaned.append(target_ip)
        self.state.detection_level = max(0, self.state.detection_level - 30)
        p(f"\n  {C.LGREEN}Logs cleaned! Detection -30%{C.RESET}")
        self.state.add_xp(30)
        print()

    def cmd_cat(self, args):
        if not args:
            p("  [USAGE] cat <file>", C.LYELLOW)
            return
        filename = args[0]
        if filename not in self.state.files:
            p(f"  [ERROR] '{filename}' not found.", C.LRED)
            return

        file_contents = {
            "readme.txt": "Welcome to CyberOS. Type 'help' to get started.",
            "notes.txt": "TODO:\n- Upgrade tools\n- Complete missions\n- Don't get caught!",
            "router_config.txt": "SSID=HomeNetwork\nWPA2_KEY=mysecretkey123\nADMIN_PASS=admin123",
            "customer_db.sql": "-- Customer DB: 15,342 records\nCREATE TABLE customers (id, name, email, cc);",
            "emails.txt": "From: ceo@business.com\nPassword is still P@ssw0rd...",
            "student_records.db": "-- 45,000 student records (names, SSNs, grades)",
            "research_data.zip": "[Encrypted research - 147 papers]",
            "financial_reports.xlsx": "Q1: $45M | Q2: $52M | Profit: $12.5M",
            "employee_data.csv": "John Smith,CEO,$500k,123-45-6789\n... 2,847 records",
            "trade_secrets.doc": "[CLASSIFIED] Project Nexus: AI market manipulation",
            "classified_intel.enc": "[TOP SECRET - AES-256 encrypted]",
            "agent_list.gpg": "[PGP - 200+ field agents - LIVES AT RISK]",
            "operation_files.tar.gz": "[Mission briefings, surveillance - 890 MB]",
            "transaction_logs.db": "TXN001: $50k -> Offshore #4421\nTXN003: $1M -> [REDACTED]",
            "account_data.enc": "[Banking data - 500k accounts - $2.8B assets]",
            "market_users.db": "-- Dark web: 25k accounts with BTC wallets",
            "crypto_wallets.dat": "BTC: 142.5 | ETH: 3,500 | Total: ~$8.5M",
            "sat_telemetry.dat": "Orbit: LEO 400km | Freq: 2.4GHz encrypted",
            "comm_encryption.key": "-----BEGIN RSA PRIVATE KEY-----\n[TRUNCATED]",
            "orbital_data.bin": "[TLE data for 200+ satellites]",
        }

        content = file_contents.get(filename, f"[Contents of {filename}]")
        print()
        gradient_print(f"  ─── {filename} ───", (100, 200, 255), (50, 100, 200))
        for line in content.split('\n'):
            decrypt_animation(line, 0.02)
        gradient_print(f"  ─── EOF ───", (50, 100, 200), (100, 200, 255))
        print()

    def cmd_inventory(self, args):
        clear_screen()
        print()
        gradient_print("  ═══ INVENTORY ════════════════════════════════════", (255, 200, 0), (255, 100, 0))
        print()
        p(f"  {C.BOLD}{C.ORANGE}TOOLS{C.RESET}")
        for tool in self.state.tools:
            p(f"    {C.LGREEN}+{C.RESET} {tool}")
        print()
        p(f"  {C.BOLD}{C.LCYAN}FILES{C.RESET}")
        for f in self.state.files:
            p(f"    {C.LBLUE}>{C.RESET} {f}")
        if self.state.backdoors:
            print()
            p(f"  {C.BOLD}{C.LRED}BACKDOORS{C.RESET}")
            for bd in self.state.backdoors:
                p(f"    {C.LRED}!{C.RESET} {bd}")
        if self.state.known_passwords:
            print()
            p(f"  {C.BOLD}{C.LMAGENTA}PASSWORDS{C.RESET}")
            for ip, pwd in self.state.known_passwords.items():
                p(f"    {C.LMAGENTA}@{C.RESET} {ip} : {C.LGREEN}{pwd}{C.RESET}")
        if self.state.intercepted_data:
            print()
            p(f"  {C.BOLD}{C.LYELLOW}INTERCEPTED{C.RESET}")
            for data in self.state.intercepted_data:
                p(f"    {C.LYELLOW}~{C.RESET} {data}")
        print()

    def cmd_shop(self, args):
        clear_screen()
        print()
        gradient_print("  ═══ BLACK MARKET ═════════════════════════════════", (200, 0, 255), (100, 0, 200))
        fire_text("        ★ BLACK MARKET SHOP ★")
        p(f"\n  {C.GOLD}Balance: ${self.state.money:,}{C.RESET}\n")

        type_colors = {"tool": C.LRED, "service": C.LCYAN, "upgrade": C.LYELLOW}
        for item_id, item in self.state.shop_items.items():
            owned = item_id in self.state.tools
            if item_id == "vpn":
                owned = self.state.vpn_active
            tc = type_colors.get(item["type"], C.LWHITE)
            status = f"{C.DIM}[OWNED]{C.RESET}" if owned else ""
            if item_id == "proxy_chain":
                status = f"{C.DIM}[x{self.state.proxy_chains}]{C.RESET}"
            elif item_id == "botnet_node":
                status = f"{C.DIM}[{self.state.botnet_size}]{C.RESET}"
            p(f"    {tc}{item_id:<18}{C.RESET}{C.GOLD}${item['price']:<8}{C.RESET}{C.DIM}{item['desc']}{C.RESET}  {status}")
        p(f"\n  Type {C.LGREEN}buy <item>{C.RESET} to purchase.")
        print()

    def cmd_buy(self, args):
        if not args:
            p("  [USAGE] buy <item>", C.LYELLOW)
            return
        item_id = args[0].lower()
        if item_id not in self.state.shop_items:
            p(f"  [ERROR] Unknown item '{item_id}'.", C.LRED)
            return
        item = self.state.shop_items[item_id]
        if item["type"] == "tool" and item_id in self.state.tools:
            p(f"  [INFO] Already own {item_id}.", C.LYELLOW)
            return
        if self.state.money < item["price"]:
            p(f"  [ERROR] Need ${item['price']:,}, have ${self.state.money:,}.", C.LRED)
            return
        self.state.money -= item["price"]
        if item["type"] == "tool":
            self.state.tools.append(item_id)
            p(f"  {C.LGREEN}Purchased {item_id}!{C.RESET}")
        elif item_id == "vpn":
            self.state.vpn_active = True
            p(f"  {C.LGREEN}VPN activated!{C.RESET}")
        elif item_id == "proxy_chain":
            self.state.proxy_chains += 1
            p(f"  {C.LGREEN}Proxy +1 (total: {self.state.proxy_chains}){C.RESET}")
        elif item_id == "botnet_node":
            self.state.botnet_size += 10
            p(f"  {C.LGREEN}+10 bots (total: {self.state.botnet_size}){C.RESET}")
        else:
            p(f"  {C.LGREEN}Purchased {item_id}!{C.RESET}")
        p(f"  {C.GOLD}Balance: ${self.state.money:,}{C.RESET}")

    def cmd_missions(self, args):
        clear_screen()
        print()
        gradient_print("  ═══ MISSION BOARD ════════════════════════════════", (255, 215, 0), (255, 140, 0))
        print()
        for m in self.missions.missions:
            if m["completed"]:
                status = f"{C.LGREEN}[COMPLETED]{C.RESET}"
                title_color = C.DIM
            elif m["min_level"] > self.state.level:
                status = f"{C.LRED}[LOCKED Lvl {m['min_level']}]{C.RESET}"
                title_color = C.DIM
            else:
                status = f"{C.LYELLOW}[AVAILABLE]{C.RESET}"
                title_color = C.BOLD + C.LWHITE

            p(f"  {title_color}{m['title']}{C.RESET}  {status}")
            p(f"    {C.DIM}{m['description']}{C.RESET}")
            p(f"    {C.STEEL}Target:{C.RESET} {m['target']}  {C.STEEL}|{C.RESET}  {C.GOLD}${m['reward_money']:,}{C.RESET} + {C.LCYAN}{m['reward_xp']} XP{C.RESET}")
            for obj in m["objectives"]:
                p(f"      {C.STEEL}-{C.RESET} {obj}")
            print()

    def cmd_vpn(self, args):
        if self.state.vpn_active:
            self.state.vpn_active = False
            p(f"  {C.LRED}VPN disconnected. IP exposed!{C.RESET}")
        else:
            self.state.vpn_active = True
            fake_ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            p(f"  {C.LGREEN}VPN connected! Spoofed IP: {fake_ip}{C.RESET}")

    def cmd_proxy(self, args):
        print()
        p(f"  {C.BOLD}Proxy Chains: {self.state.proxy_chains}{C.RESET}")
        if self.state.proxy_chains > 0:
            countries = ["Romania", "Russia", "Brazil", "Japan", "Sweden", "Iceland", "Panama", "Switzerland"]
            for i in range(self.state.proxy_chains):
                fake_ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
                country = random.choice(countries)
                p(f"    {C.LCYAN}Chain {i+1}:{C.RESET} {fake_ip} ({C.LYELLOW}{country}{C.RESET})")
        else:
            p("  No chains configured.", C.DIM)
        print()

    def cmd_encrypt(self, args):
        if not args:
            p("  [USAGE] encrypt <file>", C.LYELLOW)
            return
        if args[0] not in self.state.files:
            p(f"  [ERROR] File not found.", C.LRED)
            return
        type_loading(f"Encrypting {args[0]} (AES-256)", 1.5)
        p(f"  {C.LGREEN}Encrypted.{C.RESET}")
        self.state.add_xp(5)

    def cmd_shred(self, args):
        if not args:
            p("  [USAGE] shred <file>", C.LYELLOW)
            return
        if args[0] not in self.state.files:
            p(f"  [ERROR] File not found.", C.LRED)
            return
        type_loading(f"Shredding {args[0]} (35-pass)", 2)
        self.state.files.remove(args[0])
        p(f"  {C.LGREEN}Destroyed.{C.RESET}")

    def cmd_whoami(self, args):
        print()
        p(f"  {C.STEEL}Alias:{C.RESET}     {C.BOLD}{C.LCYAN}{self.state.player_name}{C.RESET}")
        p(f"  {C.STEEL}Real IP:{C.RESET}   {self.state.ip_address}")
        if self.state.vpn_active:
            p(f"  {C.STEEL}VPN IP:{C.RESET}    {random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}")
        p(f"  {C.STEEL}Network:{C.RESET}   {self.state.current_network}")
        p(f"  {C.STEEL}Level:{C.RESET}     {self.state.level}")
        clearance = "LOW" if self.state.level < 3 else ("MEDIUM" if self.state.level < 5 else "HIGH")
        clearance_color = C.LGREEN if clearance == "LOW" else (C.LYELLOW if clearance == "MEDIUM" else C.LRED)
        p(f"  {C.STEEL}Clearance:{C.RESET} {clearance_color}{clearance}{C.RESET}")
        print()

    def cmd_time(self, args):
        p(f"  {C.LCYAN}System Time:{C.RESET} {time.strftime('%Y-%m-%d %H:%M:%S')}")

    def cmd_history(self, args):
        print()
        start = max(0, len(self.command_history) - 20)
        for i, cmd in enumerate(self.command_history[start:], start + 1):
            p(f"  {C.DIM}{i:>4}{C.RESET}  {cmd}")
        print()

    def cmd_note(self, args):
        if not args:
            p("  [USAGE] note <text>", C.LYELLOW)
            return
        text = ' '.join(args)
        ts = time.strftime('%H:%M:%S')
        self.state.notes.append(f"[{ts}] {text}")
        p(f"  {C.LGREEN}Note saved.{C.RESET}")

    def cmd_notes(self, args):
        print()
        if not self.state.notes:
            p("  (empty) Use 'note <text>' to add.", C.DIM)
        for note in self.state.notes:
            p(f"    {C.LCYAN}{note}{C.RESET}")
        print()

    def cmd_crypto(self, args):
        btc_usd = self.state.crypto_wallet * 43000
        print()
        neon_box(f"BTC: {self.state.crypto_wallet:.6f}  |  ${btc_usd:,.2f}", C.ORANGE)
        print()

    def cmd_leaderboard(self, args):
        clear_screen()
        print()
        gradient_print("  ═══ HACKER LEADERBOARD ═══════════════════════════", (255, 215, 0), (255, 100, 0))
        print()
        hackers = [
            ("ZeroCool", random.randint(5000, 99999), random.randint(5, 10)),
            ("AcidBurn", random.randint(5000, 99999), random.randint(5, 10)),
            ("Phantom", random.randint(3000, 50000), random.randint(4, 9)),
            (self.state.player_name, self.state.reputation, self.state.level),
            ("N3tRunner", random.randint(500, 20000), random.randint(2, 7)),
            ("DarkMatter", random.randint(100, 10000), random.randint(1, 6)),
        ]
        hackers.sort(key=lambda x: x[1], reverse=True)
        rank_colors = [C.GOLD, C.SILVER, C.BRONZE]
        for i, (name, rep, lvl) in enumerate(hackers, 1):
            rc = rank_colors[i-1] if i <= 3 else C.LWHITE
            you = f" {C.NEON_PINK}<-- YOU{C.RESET}" if name == self.state.player_name else ""
            p(f"  {rc}{i:<4}{C.RESET} {C.BOLD}{name:<18}{C.RESET} {C.LMAGENTA}{rep:<10}{C.RESET} Lvl {lvl}{you}")
        print()

    def cmd_netmap(self, args):
        clear_screen()
        network_map_animation()

    def cmd_whois(self, args):
        if not args:
            p("  [USAGE] whois <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        if target_ip not in self.state.available_targets:
            p(f"  [ERROR] No records.", C.LRED)
            return
        target = self.state.available_targets[target_ip]
        print()
        glitch_text(f"  WHOIS - {target_ip}")
        print()
        p(f"  {C.STEEL}Name:{C.RESET}       {C.LWHITE}{target['name']}{C.RESET}")
        p(f"  {C.STEEL}OS:{C.RESET}         {target['os']}")
        p(f"  {C.STEEL}Services:{C.RESET}   {', '.join(target.get('services', []))}")
        fw = f"{C.LYELLOW}Yes (Lvl {target.get('firewall_level', 0)}){C.RESET}" if target['firewall'] else f"{C.LGREEN}No{C.RESET}"
        p(f"  {C.STEEL}Firewall:{C.RESET}   {fw}")
        status = f"{C.LGREEN}Compromised{C.RESET}" if target['compromised'] else f"{C.LRED}Secured{C.RESET}"
        p(f"  {C.STEEL}Status:{C.RESET}     {status}")
        print()

    def cmd_dns(self, args):
        if not args:
            p("  [USAGE] dns <domain>", C.LYELLOW)
            return
        domain = args[0]
        print()
        p(f"  {C.BOLD}DNS Lookup: {domain}{C.RESET}")
        p(f"  {C.LCYAN}A{C.RESET}      {random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}")
        p(f"  {C.LCYAN}MX{C.RESET}     mail.{domain}")
        p(f"  {C.LCYAN}NS{C.RESET}     ns1.{domain}")
        print()

    def cmd_phish(self, args):
        if "social_eng" not in self.state.tools:
            p("  [ERROR] Social engineering toolkit needed.", C.LRED)
            return
        if not args:
            p("  [USAGE] phish <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        if target_ip not in self.state.available_targets:
            p(f"  [ERROR] Unknown target.", C.LRED)
            return
        clear_screen()
        self.state.increase_detection(8)
        print()
        glitch_text(f"  PHISHING ATTACK - {target_ip}")
        print()
        type_loading("Cloning website", 1.5)
        type_loading("Sending phishing emails", 2)
        type_loading("Waiting for victims", 3)
        caught = random.randint(1, 10)
        if caught >= 3:
            target = self.state.available_targets[target_ip]
            p(f"\n  {C.LGREEN}{caught} employees phished! Credentials captured.{C.RESET}")
            self.state.known_passwords[target_ip] = target["password"]
            self.state.add_xp(60)
            self.state.money += 300
        else:
            p(f"\n  {C.LRED}Only {caught} clicked. Not enough.{C.RESET}")
        print()

    def cmd_ddos(self, args):
        if "ddos_cannon" not in self.state.tools:
            p("  [ERROR] DDoS cannon needed.", C.LRED)
            return
        if self.state.botnet_size < 10:
            p("  [ERROR] Need 10+ botnet nodes.", C.LRED)
            return
        if not args:
            p("  [USAGE] ddos <ip>", C.LYELLOW)
            return
        clear_screen()
        self.state.increase_detection(25)
        print()
        glitch_text(f"  DDoS ATTACK - {args[0]}")
        p(f"  {C.BG_DARK_RED}{C.LWHITE} LAUNCHING {self.state.botnet_size} BOTS {C.RESET}")
        print()
        for i in range(15):
            traffic = random.randint(100, 9999)
            sys.stdout.write(f"\r  {C.LRED}[ATTACK]{C.RESET} Bots: {self.state.botnet_size} | Traffic: {C.LYELLOW}{traffic} Gbps{C.RESET}")
            sys.stdout.flush()
            time.sleep(0.3)
        print("\n")
        p(f"  {C.LGREEN}Target DOWN!{C.RESET}")
        self.state.add_xp(40)
        print()

    def cmd_wifihack(self, args):
        if "aircrack" not in self.state.tools:
            p("  [ERROR] Aircrack needed.", C.LRED)
            return
        clear_screen()
        print()
        glitch_text("  WiFi CRACKER")
        print()
        networks = [
            ("HomeNetwork_5G", "WPA2", random.randint(-30, -90)),
            ("CoffeeShop", "OPEN", random.randint(-30, -90)),
            ("NETGEAR-" + str(random.randint(1000, 9999)), "WPA2", random.randint(-30, -90)),
            ("FBI_Van", "WPA3", random.randint(-30, -90)),
        ]
        p(f"  {C.BOLD}{'SSID':<25}{'SEC':<8}{'SIGNAL'}{C.RESET}")
        for ssid, sec, sig in networks:
            sec_color = C.LGREEN if sec == "OPEN" else (C.LYELLOW if sec == "WPA2" else C.LRED)
            p(f"  {C.LWHITE}{ssid:<25}{sec_color}{sec:<8}{C.RESET}{sig} dBm")
            time.sleep(0.2)
        print()
        target = input(f"  {C.LCYAN}SSID to crack (or 'cancel'):{C.RESET} ").strip()
        if target == 'cancel':
            return
        type_loading("Capturing handshake", 3)
        hacker_progress_bar("Cracking WPA2...", 4)
        if random.randint(1, 100) <= 65:
            key = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
            neon_box(f"WiFi KEY: {key}", C.LGREEN)
            self.state.add_xp(35)
            self.state.money += 100
        else:
            p(f"  {C.LRED}[FAIL] Could not crack.{C.RESET}")
        print()

    def cmd_mine(self, args):
        if "crypto_miner" not in self.state.tools:
            p("  [ERROR] Crypto miner needed.", C.LRED)
            return
        if not args:
            p("  [USAGE] mine <ip>", C.LYELLOW)
            return
        target_ip = args[0]
        if target_ip not in self.state.available_targets or not self.state.available_targets[target_ip]["compromised"]:
            p("  [ERROR] Target not compromised.", C.LRED)
            return
        print()
        type_loading(f"Deploying miner on {target_ip}", 1.5)
        mined = 0.0
        for i in range(15):
            amount = random.uniform(0.00001, 0.0005)
            mined += amount
            hashrate = random.uniform(10, 500)
            sys.stdout.write(f"\r  {C.ORANGE}[MINING]{C.RESET} {hashrate:.1f} MH/s | {C.GOLD}{mined:.6f} BTC{C.RESET}")
            sys.stdout.flush()
            time.sleep(0.5)
        self.state.crypto_wallet += mined
        print(f"\n\n  {C.GOLD}Mined {mined:.6f} BTC (${mined * 43000:,.2f}){C.RESET}")
        self.state.add_xp(20)
        self.state.increase_detection(5)
        print()

    def cmd_analyze(self, args):
        if "forensics" not in self.state.tools:
            p("  [ERROR] Forensics toolkit needed.", C.LRED)
            return
        if not args or args[0] not in self.state.files:
            p("  [ERROR] File not found.", C.LRED)
            return
        clear_screen()
        print()
        glitch_text(f"  FORENSIC ANALYSIS - {args[0]}")
        print()
        type_loading("Analyzing structure", 1)
        type_loading("Extracting metadata", 1)
        type_loading("Hash verification", 0.8)
        print()
        file_hash = hashlib.sha256(args[0].encode()).hexdigest()
        p(f"  {C.STEEL}SHA-256:{C.RESET}   {C.DIM}{file_hash}{C.RESET}")
        p(f"  {C.STEEL}Size:{C.RESET}      {random.randint(100, 50000)} KB")
        p(f"  {C.STEEL}Author:{C.RESET}    {random.choice(['admin', 'root', 'system', 'unknown'])}")
        p(f"  {C.STEEL}Encrypted:{C.RESET} {random.choice(['Yes (AES-256)', 'No', 'Partial'])}")
        self.state.add_xp(15)
        print()

    def cmd_spoof(self, args):
        new_mac = ':'.join(f'{random.randint(0, 255):02x}' for _ in range(6))
        type_loading("Spoofing MAC address", 1.5)
        p(f"  {C.LGREEN}New MAC: {new_mac}{C.RESET}")
        self.state.detection_level = max(0, self.state.detection_level - 5)

    # ========== OWNER PANEL ==========

    def cmd_owner_panel(self, args):
        SECRET = "override-gamma-7"
        if not args or ' '.join(args) != SECRET:
            p("  [ERROR] Unknown command. Type 'help'.", C.LRED)
            return
        clear_screen()
        while True:
            print()
            gradient_print("  ═══ OWNER PANEL ══════════════════════════════════", (255, 0, 100), (200, 0, 200))
            print()
            options = [
                "1. Set money", "2. Set level", "3. Unlock all tools",
                "4. Compromise all", "5. Reset detection", "6. Complete missions",
                "7. Add XP", "8. Set reputation", "9. Give tool",
                "10. Reset game", "11. Add crypto", "12. GOD MODE",
                "0. Exit panel"
            ]
            for opt in options:
                p(f"    {C.LMAGENTA}{opt}{C.RESET}")
            print()
            choice = input(f"  {C.NEON_PINK}OWNER >>{C.RESET} ").strip()

            if choice == "1":
                try:
                    self.state.money = int(input("  $: "))
                    p(f"  {C.LGREEN}OK{C.RESET}")
                except ValueError:
                    p("  Bad input.", C.LRED)
            elif choice == "2":
                try:
                    self.state.level = int(input("  Level: "))
                    self.state.xp_to_next = int(100 * (1.5 ** (self.state.level - 1)))
                    p(f"  {C.LGREEN}OK{C.RESET}")
                except ValueError:
                    p("  Bad input.", C.LRED)
            elif choice == "3":
                all_t = [k for k, v in self.state.shop_items.items() if v["type"] == "tool"]
                for t in all_t:
                    if t not in self.state.tools:
                        self.state.tools.append(t)
                p(f"  {C.LGREEN}All tools unlocked!{C.RESET}")
            elif choice == "4":
                for ip, t in self.state.available_targets.items():
                    t["compromised"] = True
                    self.state.known_passwords[ip] = t["password"]
                p(f"  {C.LGREEN}All compromised!{C.RESET}")
            elif choice == "5":
                self.state.detection_level = 0
                self.state.detected = False
                p(f"  {C.LGREEN}Detection reset.{C.RESET}")
            elif choice == "6":
                for m in self.missions.missions:
                    if not m["completed"]:
                        m["completed"] = True
                        self.state.completed_missions.append(m["id"])
                        self.state.money += m["reward_money"]
                        self.state.reputation += m["reward_rep"]
                p(f"  {C.LGREEN}All missions done!{C.RESET}")
            elif choice == "7":
                try:
                    self.state.add_xp(int(input("  XP: ")))
                except ValueError:
                    p("  Bad input.", C.LRED)
            elif choice == "8":
                try:
                    self.state.reputation = int(input("  Rep: "))
                    p(f"  {C.LGREEN}OK{C.RESET}")
                except ValueError:
                    p("  Bad input.", C.LRED)
            elif choice == "9":
                tool = input("  Tool: ").strip().lower()
                if tool and tool not in self.state.tools:
                    self.state.tools.append(tool)
                    p(f"  {C.LGREEN}Added.{C.RESET}")
            elif choice == "10":
                if input("  Reset? (yes): ").strip() == "yes":
                    self.state = GameState()
                    self.missions = MissionSystem()
                    p(f"  {C.LGREEN}Reset!{C.RESET}")
            elif choice == "11":
                try:
                    self.state.crypto_wallet += float(input("  BTC: "))
                    p(f"  {C.LGREEN}OK{C.RESET}")
                except ValueError:
                    p("  Bad input.", C.LRED)
            elif choice == "12":
                self.state.money = 999999
                self.state.level = 10
                self.state.reputation = 99999
                self.state.detection_level = 0
                self.state.vpn_active = True
                self.state.proxy_chains = 5
                self.state.botnet_size = 100
                self.state.crypto_wallet = 100.0
                all_t = ["nmap", "ping"] + [k for k, v in self.state.shop_items.items() if v["type"] == "tool"]
                self.state.tools = list(set(all_t))
                p(f"  {C.NEON_PINK}{C.BOLD}GOD MODE ACTIVATED!{C.RESET}")
            elif choice == "0":
                clear_screen()
                self.show_banner()
                return

    # ========== MISSION CHECK ==========

    def _check_missions(self, target_ip):
        for m in self.missions.missions:
            if m["target"] == target_ip and not m["completed"]:
                m["completed"] = True
                self.state.completed_missions.append(m["id"])
                self.state.money += m["reward_money"]
                self.state.reputation += m["reward_rep"]
                self.state.add_xp(m["reward_xp"])
                print()
                gradient_print("  ★ ═══════════════════════════════════════ ★", (255, 215, 0), (255, 100, 0))
                fire_text(f"       MISSION COMPLETE: {m['title']}")
                p(f"  {C.GOLD}+${m['reward_money']:,}{C.RESET} {C.LCYAN}+{m['reward_xp']} XP{C.RESET} {C.LMAGENTA}+{m['reward_rep']} REP{C.RESET}")
                gradient_print("  ★ ═══════════════════════════════════════ ★", (255, 100, 0), (255, 215, 0))

                if all(mi["completed"] for mi in self.missions.missions):
                    self._victory_screen()

    def _victory_screen(self):
        clear_screen()
        matrix_rain(2)
        clear_screen()
        print()
        rainbow_text("  ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★")
        gradient_print("       ALL MISSIONS COMPLETED!", (0, 255, 0), (0, 255, 255))
        gradient_print("        LEGENDARY HACKER STATUS", (255, 215, 0), (255, 100, 0))
        rainbow_text("  ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★")
        print()
        p(f"  {C.LWHITE}Level: {self.state.level} | Money: ${self.state.money:,} | Rep: {self.state.reputation}{C.RESET}")
        print()
        input(f"  {C.DIM}[Press ENTER for free mode]{C.RESET}")
        clear_screen()
        self.show_banner()

    # ========== DETECTION ==========

    def check_detection(self):
        if self.state.detected:
            clear_screen()
            matrix_rain(1)
            print()
            p(f"  {C.BG_RED}{C.LWHITE}{C.BOLD}{'=' * 50}{C.RESET}")
            fire_text("             B U S T E D !")
            p(f"  {C.BG_RED}{C.LWHITE}{C.BOLD}   YOUR IDENTITY HAS BEEN EXPOSED   {C.RESET}")
            p(f"  {C.BG_RED}{C.LWHITE}{C.BOLD}{'=' * 50}{C.RESET}")
            print()
            p(f"  {C.LWHITE}Level: {self.state.level} | Money: ${self.state.money:,}{C.RESET}")
            p(f"  {C.LWHITE}Missions: {len(self.state.completed_missions)}/{len(self.missions.missions)}{C.RESET}")
            print()

            # Save before game over
            save_game(self.state, self.missions, self.state.player_name)

            choice = input(f"  {C.LYELLOW}Play again? (y/n):{C.RESET} ").strip().lower()
            if choice == 'y':
                self.state = GameState()
                self.missions = MissionSystem()
                self.run()
            else:
                p(f"\n  {C.LCYAN}Thanks for playing!{C.RESET}\n")
                sys.exit(0)

    # ========== COMMAND ROUTER ==========

    def process_command(self, raw_input):
        parts = raw_input.strip().split()
        if not parts:
            return
        cmd = parts[0].lower()
        args = parts[1:]
        self.command_history.append(raw_input)
        save_command_to_history(self.state.player_name, raw_input)

        commands = {
            "help": self.cmd_help, "status": self.cmd_status, "targets": self.cmd_targets,
            "missions": self.cmd_missions, "shop": self.cmd_shop, "buy": self.cmd_buy,
            "inventory": self.cmd_inventory, "tutorial": lambda a: self.show_tutorial(),
            "save": self.cmd_save, "whoami": self.cmd_whoami, "time": self.cmd_time,
            "history": self.cmd_history, "note": self.cmd_note, "notes": self.cmd_notes,
            "crypto": self.cmd_crypto, "leaderboard": self.cmd_leaderboard,
            "clear": lambda a: clear_screen(), "cls": lambda a: clear_screen(),
            "exit": lambda a: self.quit_game(), "quit": lambda a: self.quit_game(),
            "nmap": self.cmd_nmap, "ping": self.cmd_ping, "traceroute": self.cmd_traceroute,
            "connect": self.cmd_connect, "disconnect": self.cmd_disconnect,
            "netmap": self.cmd_netmap, "whois": self.cmd_whois, "dns": self.cmd_dns,
            "crack": self.cmd_crack, "firewall_bypass": self.cmd_firewall_bypass,
            "exploit": self.cmd_exploit, "sqlinject": self.cmd_sqlinject,
            "sniff": self.cmd_sniff, "bruteforce": self.cmd_bruteforce,
            "phish": self.cmd_phish, "ddos": self.cmd_ddos, "wifihack": self.cmd_wifihack,
            "download": self.cmd_download, "backdoor": self.cmd_backdoor,
            "clean_logs": self.cmd_clean_logs, "cat": self.cmd_cat,
            "mine": self.cmd_mine, "analyze": self.cmd_analyze,
            "vpn": self.cmd_vpn, "proxy": self.cmd_proxy,
            "encrypt": self.cmd_encrypt, "shred": self.cmd_shred, "spoof": self.cmd_spoof,
            "sudo": self.cmd_owner_panel,
        }

        if cmd in commands:
            commands[cmd](args)
            self.auto_save()
        else:
            p(f"  {C.LRED}[ERROR] Unknown: '{cmd}'. Type 'help'.{C.RESET}")

    def quit_game(self):
        clear_screen()
        print()
        gradient_print("  ═══════════════════════════════════════════", (100, 100, 100), (50, 50, 50))
        p(f"  {C.LWHITE}Session terminated.{C.RESET}")
        type_loading("Saving progress", 1)
        save_game(self.state, self.missions, self.state.player_name)
        type_loading("Wiping session data", 0.8)
        type_loading("Destroying keys", 0.5)
        print()
        p(f"  {C.LGREEN}Saved to: {get_user_dir(self.state.player_name)}{C.RESET}")
        p(f"  {C.LCYAN}Goodbye, {self.state.player_name}.{C.RESET}")
        gradient_print("  ═══════════════════════════════════════════", (50, 50, 50), (100, 100, 100))
        print()
        sys.exit(0)

    # ========== MAIN ==========

    def run(self):
        # Profile selection
        result = self.profile_menu()

        if result == "new":
            self.boot_sequence()
            self.login_screen()
        elif result == "loaded":
            self.boot_sequence()
            self.login_screen()

        clear_screen()
        self.show_banner()

        # Tutorial prompt
        if not self.state.tutorial_done:
            choice = input(f"  {C.LCYAN}First time? Tutorial? (y/n):{C.RESET} ").strip().lower()
            if choice == 'y':
                self.show_tutorial()
            else:
                self.state.tutorial_done = True
                p(f"  Type {C.LGREEN}'tutorial'{C.RESET} anytime to learn.\n")

        # Initial save
        save_game(self.state, self.missions, self.state.player_name)

        while self.running:
            try:
                self.check_detection()
                user_input = input(self.get_prompt())
                self.process_command(user_input)
            except KeyboardInterrupt:
                print(f"\n  {C.LYELLOW}Use 'exit' to quit properly.{C.RESET}\n")
            except EOFError:
                self.quit_game()


# ============================================================
#                       START
# ============================================================
if __name__ == "__main__":
    game = HackingSimulator()
    game.run()