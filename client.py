import socket
import json
import sys
import os
import time
import random
import hashlib
import getpass
import threading
from datetime import datetime

# ============================================================
#                   CROSS-PLATFORM ANSI
# ============================================================

def enable_ansi():
    if os.name == 'nt':
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleMode(
                ctypes.windll.kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            pass
        if any(os.environ.get(v) for v in ['WT_SESSION', 'TERM_PROGRAM', 'ANSICON']):
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
        RED="\033[91m"; GREEN="\033[92m"; YELLOW="\033[93m"; BLUE="\033[94m"
        MAGENTA="\033[95m"; CYAN="\033[96m"; WHITE="\033[97m"
        ORANGE="\033[38;5;208m"; GOLD="\033[38;5;220m"; PINK="\033[38;5;205m"
        PURPLE="\033[38;5;129m"; LIME="\033[38;5;118m"; TEAL="\033[38;5;30m"
        STEEL="\033[38;5;244m"; SILVER="\033[38;5;250m"
        CRIMSON="\033[38;5;196m"; EMERALD="\033[38;5;46m"; VIOLET="\033[38;5;135m"
        CORAL="\033[38;5;209m"; MINT="\033[38;5;121m"; BRONZE="\033[38;5;136m"
        NEON_GREEN="\033[38;5;46m"; NEON_PINK="\033[38;5;198m"
        DARK_GREEN="\033[38;5;22m"; DARK_RED="\033[38;5;88m"
        BG_RED="\033[41m"; BG_GREEN="\033[42m"; BG_DARK="\033[48;5;235m"
        BG_DARK_RED="\033[48;5;52m"; BG_DARK_GREEN="\033[48;5;22m"
        BOLD="\033[1m"; DIM="\033[2m"; ITALIC="\033[3m"
        UNDERLINE="\033[4m"; RESET="\033[0m"
    else:
        RED=GREEN=YELLOW=BLUE=MAGENTA=CYAN=WHITE=""
        ORANGE=GOLD=PINK=PURPLE=LIME=TEAL=STEEL=SILVER=""
        CRIMSON=EMERALD=VIOLET=CORAL=MINT=BRONZE=""
        NEON_GREEN=NEON_PINK=DARK_GREEN=DARK_RED=""
        BG_RED=BG_GREEN=BG_DARK=BG_DARK_RED=BG_DARK_GREEN=""
        BOLD=DIM=ITALIC=UNDERLINE=RESET=""

    @staticmethod
    def rgb(r, g, b):
        return f"\033[38;2;{r};{g};{b}m" if USE_COLORS else ""

    @staticmethod
    def gradient(text, start, end):
        if not USE_COLORS:
            return text
        result = ""
        l = max(len(text), 1)
        for i, ch in enumerate(text):
            ratio = i / l
            r = int(start[0] + (end[0]-start[0])*ratio)
            g = int(start[1] + (end[1]-start[1])*ratio)
            b = int(start[2] + (end[2]-start[2])*ratio)
            result += f"\033[38;2;{r};{g};{b}m{ch}"
        return result + "\033[0m"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def p(text, color=""):
    if USE_COLORS and color:
        print(color + text + C.RESET)
    else:
        print(text)

def get_terminal_width():
    try:
        return os.get_terminal_size().columns
    except Exception:
        return 80

# ============================================================
#                    TEXT EFFECTS
# ============================================================

def type_text(text, speed=0.02, color=""):
    c = color if USE_COLORS else ""
    r = C.RESET if USE_COLORS else ""
    for ch in text:
        sys.stdout.write(c + ch + r)
        sys.stdout.flush()
        time.sleep(speed)
    print()

def type_loading(message, duration=1.5):
    frames = ["|", "/", "-", "\\"]
    end = time.time() + duration
    i = 0
    while time.time() < end:
        sys.stdout.write(f"\r  {C.CYAN}{frames[i%4]}{C.RESET} {message}...")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write(f"\r  {C.GREEN}+{C.RESET} {message}... {C.GREEN}OK{C.RESET}\n")
    sys.stdout.flush()

def progress_bar(message, duration=2, width=35):
    p(f"  {message}", C.YELLOW)
    for i in range(width + 1):
        pct = (i / width) * 100
        col = C.GREEN if pct < 50 else (C.YELLOW if pct < 80 else C.RED)
        bar = f"{col}{'#' * i}{C.STEEL}{'-' * (width - i)}{C.RESET}"
        sys.stdout.write(f"\r  [{bar}] {C.WHITE}{pct:.0f}%{C.RESET}")
        sys.stdout.flush()
        time.sleep(duration / width)
    print()

def hacker_bar(message, duration=2, width=35):
    p(f"  {message}", C.YELLOW)
    hx = "0123456789ABCDEF"
    for i in range(width + 1):
        pct = (i / width) * 100
        bar = f"{C.NEON_GREEN}{'#' * i}{C.STEEL}{'-' * (width - i)}{C.RESET}"
        leak = ''.join(random.choices(hx, k=8))
        sys.stdout.write(f"\r  [{bar}] {C.WHITE}{pct:.0f}%{C.RESET} {C.DIM}{C.GREEN}0x{leak}{C.RESET}")
        sys.stdout.flush()
        time.sleep(duration / width)
    print()

def fake_data(lines=10, speed=0.04):
    hx = "0123456789ABCDEF"
    cols = [C.GREEN, C.DARK_GREEN, C.EMERALD, C.MINT]
    for _ in range(lines):
        addr = ''.join(random.choices(hx, k=8))
        data = ' '.join(''.join(random.choices(hx, k=2)) for _ in range(12))
        p(f"  {C.DIM}{random.choice(cols)}0x{addr}  {data}{C.RESET}")
        time.sleep(speed)

def matrix_rain(duration=2):
    w = min(get_terminal_width() - 2, 70)
    end = time.time() + duration
    while time.time() < end:
        line = ''.join(random.choices("01", weights=[3,1], k=w))
        p(line, C.DIM + C.GREEN)
        time.sleep(0.04)

def glitch_text(text, iters=5, speed=0.07):
    gc = "@#$%&*!?><{}[]"
    colors = [C.RED, C.GREEN, C.CYAN, C.YELLOW, C.MAGENTA, C.ORANGE]
    for i in range(iters):
        g = ""
        for j, ch in enumerate(text):
            if ch == " ":
                g += " "
            elif random.random() < (i / iters):
                g += ch
            else:
                g += random.choice(gc)
        sys.stdout.write(f"\r{random.choice(colors)}{g}{C.RESET}")
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write(f"\r{C.BOLD}{C.CYAN}{text}{C.RESET}\n")
    sys.stdout.flush()

def typing_anim(text, speed=0.03):
    for i in range(len(text) + 1):
        sys.stdout.write(f"\r  {C.GREEN}>{C.RESET} {text[:i]}{C.GREEN}_{C.RESET}")
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write(f"\r  {C.GREEN}>{C.RESET} {text} \n")
    sys.stdout.flush()

def scan_anim(target, duration=2):
    items = ["Checking ports", "Analyzing services", "Fingerprinting OS",
             "Detecting firewall", "Mapping network", "Finding vulnerabilities"]
    frames = ["|", "/", "-", "\\"]
    for item in items:
        end = time.time() + (duration / len(items))
        i = 0
        while time.time() < end:
            sys.stdout.write(f"\r  {C.CYAN}{frames[i%4]}{C.RESET} {item}...")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        sys.stdout.write(f"\r  {C.GREEN}+{C.RESET} {item}... {C.GREEN}DONE{C.RESET}\n")
        sys.stdout.flush()

def decrypt_anim(text, speed=0.02):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%"
    display = list(''.join(random.choices(chars, k=len(text))))
    for idx in range(len(text)):
        display[idx] = text[idx]
        for j in range(idx + 1, len(text)):
            display[j] = random.choice(chars) if text[j] != ' ' else ' '
        sys.stdout.write(f"\r  {C.GREEN}{''.join(display)}{C.RESET}")
        sys.stdout.flush()
        time.sleep(speed)
    sys.stdout.write(f"\r  {text}{C.RESET}\n")
    sys.stdout.flush()

def warning_flash(msg, flashes=3):
    for _ in range(flashes):
        sys.stdout.write(f"\r  {C.BG_RED}{C.WHITE}{C.BOLD} [!] {msg} [!] {C.RESET}")
        sys.stdout.flush()
        time.sleep(0.3)
        sys.stdout.write(f"\r{' ' * (len(msg) + 20)}\r")
        sys.stdout.flush()
        time.sleep(0.2)
    p(f"  {C.BG_RED}{C.WHITE}{C.BOLD} [!] {msg} [!] {C.RESET}")

def pw_crack_anim(password, duration=2):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()"
    display = ["_"] * len(password)
    delay = duration / max(len(password), 1)
    for i in range(len(password)):
        for _ in range(random.randint(5, 12)):
            display[i] = random.choice(chars)
            cracked = f"{C.GREEN}{''.join(display[:i])}{C.RESET}"
            cur = f"{C.YELLOW}{display[i]}{C.RESET}"
            rem = f"{C.STEEL}{''.join(display[i+1:])}{C.RESET}"
            sys.stdout.write(f"\r  Password: [{cracked}{cur}{rem}]")
            sys.stdout.flush()
            time.sleep(0.02)
        display[i] = password[i]
        time.sleep(delay)
    final = f"{C.GREEN}{C.BOLD}{''.join(display)}{C.RESET}"
    sys.stdout.write(f"\r  Password: [{final}]")
    sys.stdout.flush()
    print()

def neon_box(text, color=None):
    if color is None:
        color = C.CYAN
    w = len(text) + 4
    p(f"  {color}{'=' * w}{C.RESET}")
    p(f"  {color}|{C.RESET} {C.BOLD}{C.WHITE}{text}{C.RESET} {color}|{C.RESET}")
    p(f"  {color}{'=' * w}{C.RESET}")

def rainbow(text):
    cols = [C.RED, C.ORANGE, C.YELLOW, C.GREEN, C.CYAN, C.BLUE, C.MAGENTA]
    r = ""
    for i, ch in enumerate(text):
        r += cols[i % len(cols)] + ch if ch != " " else " "
    print(r + C.RESET)

def gprint(text, s, e):
    print(C.gradient(text, s, e))

def fire_text(text):
    fc = [C.rgb(255,0,0), C.rgb(255,69,0), C.rgb(255,140,0),
          C.rgb(255,165,0), C.rgb(255,200,0), C.rgb(255,255,0)]
    r = ""
    for i, ch in enumerate(text):
        r += fc[i % len(fc)] + ch
    print(r + C.RESET)

def netmap_anim():
    print()
    p("  Mapping network topology...", C.YELLOW)
    time.sleep(0.5)
    lines = [
        f"                    {C.RED}[INTERNET]{C.RESET}",
        f"                        {C.STEEL}|{C.RESET}",
        f"                    {C.ORANGE}[GATEWAY]{C.RESET}",
        f"                   {C.STEEL}/    |    \\{C.RESET}",
        f"              {C.YELLOW}[DMZ]{C.RESET}  {C.GREEN}[LAN]{C.RESET}  {C.CYAN}[WIFI]{C.RESET}",
        f"              {C.STEEL}/   \\    |      |{C.RESET}",
        f"          {C.RED}[WEB]{C.RESET} {C.BLUE}[DNS]{C.RESET} {C.MAGENTA}[DB]{C.RESET}  {C.PURPLE}[IoT]{C.RESET}",
        f"            {C.STEEL}|           |{C.RESET}",
        f"         {C.GOLD}[LOGS]{C.RESET}      {C.EMERALD}[BACKUP]{C.RESET}",
    ]
    for line in lines:
        print(line)
        time.sleep(0.25)
    print()

def epic_fail(reason=""):
    clear()
    matrix_rain(0.8)
    clear()
    print()
    p(f"  {C.BG_RED}{C.WHITE}{C.BOLD}{'='*50}{C.RESET}")
    fire_text("             E P I C   F A I L")
    p(f"  {C.BG_RED}{C.WHITE}{C.BOLD}{'='*50}{C.RESET}")
    if reason:
        p(f"  {C.RED}{reason}{C.RESET}")
    print()

def easter_egg_text():
    eggs = [
        f"  {C.MAGENTA}>>>>>>>>> PWNED BY: Anonymous <<<<<<<<<<{C.RESET}",
        f"  {C.NEON_PINK}[+] ALL YOUR BASE ARE BELONG TO US{C.RESET}",
        f"  {C.CYAN}[*] Have you tried turning it off and on again?{C.RESET}",
        f"  {C.LIME}[!] It's not a bug, it's a feature{C.RESET}",
        f"  {C.YELLOW}[#] The mitochondria is the powerhouse of the cell{C.RESET}",
        f"  {C.RED}[X] ERROR 404: YOUR SECURITY NOT FOUND{C.RESET}",
        f"  {C.GREEN}[✓] Hacking the Gibson...{C.RESET}",
        f"  {C.PURPLE}[∞] Hello, World!{C.RESET}",
    ]
    return random.choice(eggs)

# ============================================================
#                    GAME STATE
# ============================================================


class GameState:
    def __init__(self):
        self.player_name = "ghost"
        self.reputation = 0
        self.money = 1000
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
    self.faction = None
    self.faction_rank = 0
    self.heat_level = 0
    self.hacks_attempted = 0
    self.hacks_successful = 0
    self.players_hacked = []
    self.enemy_hackers = []
    self.custom_factions = {}
    self.available_targets = self._gen_targets()
    self.shop_items = {
            "hydra":{"price":300,"desc":"Brute-force cracker","type":"tool"},
            "sqlmap":{"price":500,"desc":"SQL injection tool","type":"tool"},
            "metasploit":{"price":800,"desc":"Exploit framework","type":"tool"},
            "wireshark":{"price":400,"desc":"Packet sniffer","type":"tool"},
            "john":{"price":350,"desc":"Hash cracker","type":"tool"},
            "aircrack":{"price":600,"desc":"WiFi cracker","type":"tool"},
            "rootkit":{"price":1000,"desc":"Backdoor kit","type":"tool"},
            "vpn":{"price":200,"desc":"Hide your IP","type":"service"},
            "proxy_chain":{"price":150,"desc":"Add proxy layer","type":"service"},
            "botnet_node":{"price":500,"desc":"Add 10 bots","type":"service"},
            "ram_upgrade":{"price":400,"desc":"Faster cracking","type":"upgrade"},
            "zero_day":{"price":2000,"desc":"Bypass any firewall","type":"tool"},
            "crypto_miner":{"price":750,"desc":"Mine crypto","type":"tool"},
            "social_eng":{"price":450,"desc":"Phishing toolkit","type":"tool"},
            "ddos_cannon":{"price":1200,"desc":"DDoS tool","type":"tool"},
            "forensics":{"price":600,"desc":"Forensics toolkit","type":"tool"},
            "ransomware":{"price":1500,"desc":"Encrypt target files","type":"tool"},
            "keylogger":{"price":350,"desc":"Log keystrokes","type":"tool"},
            "tor_browser":{"price":250,"desc":"Access dark web safely","type":"tool"},
            "player_tracker":{"price":800,"desc":"Track other hackers","type":"tool"},
            "honeypot":{"price":600,"desc":"Trap attackers","type":"service"},
            "firewall_upgrade":{"price":1000,"desc":"Better defense","type":"upgrade"},
            "insurance":{"price":500,"desc":"Recover from theft","type":"service"},
            "blackmail_kit":{"price":3000,"desc":"Extort targets (risky!)","type":"tool"},
        }
        self.faction_items = {
            "red_team": {"name": "Red Team", "desc": "Chaos agents", "color": C.RED, "bonus": "attack_power"},
            "blue_team": {"name": "Blue Team", "desc": "Defenders", "color": C.BLUE, "bonus": "defense"},
            "ghost_net": {"name": "Ghost Net", "desc": "Shadow collective", "color": C.MAGENTA, "bonus": "stealth"},
            "syndicate": {"name": "Syndicate", "desc": "Crime lords", "color": C.ORANGE, "bonus": "money_steal"},
        }

    def _gen_targets(self):
        return {
            "192.168.1.1":{"name":"Home Router","difficulty":1,"os":"Linux 2.6",
                "ports":{22:"SSH",80:"HTTP",443:"HTTPS"},"firewall":False,"firewall_level":0,
                "password":"admin123","loot":{"money":100,"xp":25,"files":["router_config.txt"]},
                "compromised":False,"services":["SSH","HTTP"]},
            "10.0.0.5":{"name":"Small Business Server","difficulty":2,"os":"Windows Server 2016",
                "ports":{21:"FTP",22:"SSH",80:"HTTP",3306:"MySQL"},"firewall":True,"firewall_level":1,
                "password":"P@ssw0rd","loot":{"money":500,"xp":75,"files":["customer_db.sql","emails.txt"]},
                "compromised":False,"services":["FTP","SSH","HTTP","MySQL"]},
            "172.16.0.10":{"name":"University Database","difficulty":3,"os":"Ubuntu 20.04",
                "ports":{22:"SSH",80:"HTTP",443:"HTTPS",5432:"PostgreSQL"},"firewall":True,"firewall_level":2,
                "password":"academic2024","loot":{"money":1000,"xp":150,"files":["student_records.db","research_data.zip"]},
                "compromised":False,"services":["SSH","HTTP","HTTPS","PostgreSQL"]},
            "198.51.100.20":{"name":"Dark Web Marketplace","difficulty":3,"os":"Tor Hidden (Debian)",
                "ports":{80:"HTTP",443:"HTTPS",6667:"IRC"},"firewall":True,"firewall_level":2,
                "password":"darkn3t!","loot":{"money":5000,"xp":200,"files":["market_users.db","crypto_wallets.dat"]},
                "compromised":False,"services":["HTTP","HTTPS","IRC"]},
            "10.10.10.1":{"name":"Corporate - MegaCorp","difficulty":4,"os":"Windows Server 2019",
                "ports":{22:"SSH",80:"HTTP",443:"HTTPS",445:"SMB",1433:"MSSQL",3389:"RDP"},"firewall":True,"firewall_level":3,
                "password":"C0rp$ecure!","loot":{"money":3000,"xp":300,"files":["financial_reports.xlsx","employee_data.csv","trade_secrets.doc"]},
                "compromised":False,"services":["SSH","HTTP","HTTPS","SMB","MSSQL","RDP"]},
            "10.20.30.40":{"name":"Government - ClassifiedNet","difficulty":5,"os":"Hardened Linux (SELinux)",
                "ports":{22:"SSH",443:"HTTPS",8443:"Secure Portal"},"firewall":True,"firewall_level":5,
                "password":"T0p$3cr3t!Gov","loot":{"money":10000,"xp":1000,"files":["classified_intel.enc","agent_list.gpg","operation_files.tar.gz"]},
                "compromised":False,"services":["SSH","HTTPS","Secure Portal"]},
            "203.0.113.50":{"name":"Bank of CyberCity","difficulty":5,"os":"AIX 7.2",
                "ports":{22:"SSH",443:"HTTPS",8080:"API Gateway",9090:"Admin Panel"},"firewall":True,"firewall_level":4,
                "password":"B@nkV4ult!","loot":{"money":25000,"xp":1500,"files":["transaction_logs.db","account_data.enc"]},
                "compromised":False,"services":["SSH","HTTPS","API Gateway","Admin Panel"]},
            "10.99.99.1":{"name":"Satellite Comm System","difficulty":5,"os":"VxWorks RTOS",
                "ports":{22:"SSH",8080:"Control Panel",9999:"Telemetry"},"firewall":True,"firewall_level":5,
                "password":"0rb1t@lC0mm","loot":{"money":50000,"xp":3000,"files":["sat_telemetry.dat","comm_encryption.key","orbital_data.bin"]},
                "compromised":False,"services":["SSH","Control Panel","Telemetry"]},
            # NEW TARGETS
            "192.168.100.50":{"name":"Tech Startup - TechFlow","difficulty":2,"os":"Ubuntu 18.04",
                "ports":{22:"SSH",80:"HTTP",443:"HTTPS",5000:"API"},"firewall":False,"firewall_level":0,
                "password":"startup123","loot":{"money":750,"xp":100,"files":["user_data.json","api_keys.txt"]},
                "compromised":False,"services":["SSH","HTTP","HTTPS","API"]},
            "10.1.1.1":{"name":"Hospital Network","difficulty":3,"os":"Windows Server 2016",
                "ports":{3389:"RDP",1433:"MSSQL",445:"SMB"},"firewall":True,"firewall_level":2,
                "password":"HospitalSec2024","loot":{"money":2000,"xp":200,"files":["patient_records.db","med_data.enc"]},
                "compromised":False,"services":["RDP","MSSQL","SMB"]},
            "172.20.0.1":{"name":"News Media Server","difficulty":2,"os":"Linux CentOS",
                "ports":{22:"SSH",80:"HTTP",443:"HTTPS"},"firewall":True,"firewall_level":1,
                "password":"MediaPass99","loot":{"money":600,"xp":120,"files":["article_db.sql","journalist_emails.txt"]},
                "compromised":False,"services":["SSH","HTTP","HTTPS"]},
            "10.50.50.50":{"name":"Gaming Studio Server","difficulty":3,"os":"Windows Server 2019",
                "ports":{80:"HTTP",443:"HTTPS",3306:"MySQL",27017:"MongoDB"},"firewall":True,"firewall_level":2,
                "password":"GameDev2024!","loot":{"money":1500,"xp":180,"files":["player_db.sql","source_code.zip"]},
                "compromised":False,"services":["HTTP","HTTPS","MySQL","MongoDB"]},
            "203.0.113.100":{"name":"Crypto Exchange - CoinVault","difficulty":4,"os":"Linux Ubuntu",
                "ports":{443:"HTTPS",8080:"API",9200:"Elasticsearch"},"firewall":True,"firewall_level":3,
                "password":"CryptoVault#2024","loot":{"money":15000,"xp":500,"files":["wallet_data.enc","trade_history.db"]},
                "compromised":False,"services":["HTTPS","API","Elasticsearch"]},
            "192.168.50.1":{"name":"E-commerce Platform","difficulty":3,"os":"CentOS Linux",
                "ports":{80:"HTTP",443:"HTTPS",3306:"MySQL"},"firewall":True,"firewall_level":2,
                "password":"ShopSecure123","loot":{"money":2500,"xp":220,"files":["customer_data.sql","payment_logs.txt"]},
                "compromised":False,"services":["HTTP","HTTPS","MySQL"]},
            "10.75.75.75":{"name":"Research Institute","difficulty":4,"os":"Ubuntu Server",
                "ports":{22:"SSH",443:"HTTPS",8888:"Jupyter"},"firewall":True,"firewall_level":3,
                "password":"Research#Lab99","loot":{"money":3500,"xp":400,"files":["research_data.zip","ai_models.tar.gz"]},
                "compromised":False,"services":["SSH","HTTPS","Jupyter"]},
            "198.51.100.75":{"name":"Law Firm Database","difficulty":3,"os":"Windows Server 2016",
                "ports":{1433:"MSSQL",445:"SMB",3389:"RDP"},"firewall":True,"firewall_level":2,
                "password":"LegalSec2024","loot":{"money":2000,"xp":250,"files":["case_files.db","client_info.enc"]},
                "compromised":False,"services":["MSSQL","SMB","RDP"]},
            "172.25.0.10":{"name":"Manufacturing Plant","difficulty":2,"os":"Windows Embedded",
                "ports":{502:"Modbus",80:"HTTP"},"firewall":False,"firewall_level":0,
                "password":"Factory123","loot":{"money":800,"xp":140,"files":["production_logs.csv","specs.txt"]},
                "compromised":False,"services":["Modbus","HTTP"]},
            "10.100.100.1":{"name":"Pharmaceutical Corp","difficulty":4,"os":"AIX Server",
                "ports":{22:"SSH",443:"HTTPS",8443:"Secure"},"firewall":True,"firewall_level":4,
                "password":"PharmaSec#99","loot":{"money":8000,"xp":600,"files":["clinical_trials.db","formulas.enc"]},
                "compromised":False,"services":["SSH","HTTPS","Secure"]},
        }

    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = int(self.xp_to_next * 1.5)
            print()
            gprint("  * ======================================= *", (255,215,0), (255,140,0))
            gprint(f"  *       LEVEL UP! Now Level {self.level}!          *", (255,255,0), (255,165,0))
            gprint("  * ======================================= *", (255,215,0), (255,140,0))
            print()
            time.sleep(1.5)

    def increase_detection(self, amount):
        if self.vpn_active:
            amount = amount // 2
        amount = max(1, amount - self.proxy_chains * 5)
        self.detection_level = min(100, self.detection_level + amount)
        self.heat_level = min(100, self.heat_level + amount // 2)
        if 75 <= self.detection_level < 100:
            warning_flash("DETECTION CRITICAL", 2)
        if self.detection_level >= 100:
            self.detected = True

    def to_dict(self):
        return {
            "money": self.money, "level": self.level, "xp": self.xp,
            "xp_to_next": self.xp_to_next, "reputation": self.reputation,
            "crypto_wallet": self.crypto_wallet, "tools": self.tools,
            "files": self.files, "detection_level": self.detection_level,
            "vpn_active": self.vpn_active, "proxy_chains": self.proxy_chains,
            "botnet_size": self.botnet_size, "known_passwords": self.known_passwords,
            "backdoors": self.backdoors, "intercepted_data": self.intercepted_data,
            "completed_missions": self.completed_missions, "notes": self.notes,
            "tutorial_done": self.tutorial_done, "faction": self.faction,
            "heat_level": self.heat_level, "players_hacked": self.players_hacked,
            "compromised_targets": [ip for ip, t in self.available_targets.items() if t["compromised"]],
        }

    def from_dict(self, d):
        for k in ["money","level","xp","xp_to_next","reputation","crypto_wallet",
                   "detection_level","vpn_active","proxy_chains","botnet_size","tutorial_done",
                   "heat_level","faction"]:
            if k in d:
                setattr(self, k, d[k])
        for k in ["tools","files","known_passwords","backdoors","intercepted_data",
                   "completed_missions","notes","players_hacked"]:
            if k in d:
                setattr(self, k, d[k])
        for ip in d.get("compromised_targets", []):
            if ip in self.available_targets:
                self.available_targets[ip]["compromised"] = True




class MissionSystem:
def __init__(self):
    self.missions = [
        {"id":"m1","title":"Script Kiddie's First Hack","desc":"Hack home router 192.168.1.1",
         "target":"192.168.1.1","objectives":["Scan","Crack","Exploit"],
         "reward_money":200,"reward_xp":50,"reward_rep":5,"min_level":1,"completed":False},
        {"id":"m2","title":"Data Heist","desc":"Steal customer DB from 10.0.0.5",
         "target":"10.0.0.5","objectives":["Bypass FW","Crack","Download"],
         "reward_money":1000,"reward_xp":150,"reward_rep":15,"min_level":2,"completed":False},
        {"id":"m3","title":"Academic Espionage","desc":"Hack university database",
         "target":"172.16.0.10","objectives":["Bypass FW","SQL inject","Exfiltrate"],
         "reward_money":2500,"reward_xp":300,"reward_rep":25,"min_level":3,"completed":False},
        {"id":"m4","title":"Dark Market Raid","desc":"Steal crypto from dark web",
         "target":"198.51.100.20","objectives":["Bypass FW","Steal wallets"],
         "reward_money":7500,"reward_xp":400,"reward_rep":35,"min_level":3,"completed":False},
        {"id":"m5","title":"Corporate Takedown","desc":"Steal MegaCorp secrets",
         "target":"10.10.10.1","objectives":["Bypass FW","Exploit SMB","Backdoor"],
         "reward_money":5000,"reward_xp":500,"reward_rep":50,"min_level":4,"completed":False},
        {"id":"m6","title":"Shadow Government","desc":"Infiltrate classified server",
         "target":"10.20.30.40","objectives":["Chain proxies","Bypass mil-FW","Decrypt"],
         "reward_money":15000,"reward_xp":2000,"reward_rep":100,"min_level":5,"completed":False},
        {"id":"m7","title":"The Big Score","desc":"Rob Bank of CyberCity",
         "target":"203.0.113.50","objectives":["Stealth","Crack vault","Clean logs"],
         "reward_money":50000,"reward_xp":5000,"reward_rep":200,"min_level":6,"completed":False},
        {"id":"m8","title":"Orbital Strike","desc":"Hack satellite comms",
         "target":"10.99.99.1","objectives":["Bypass RTOS","Access telemetry","Keys"],
         "reward_money":75000,"reward_xp":8000,"reward_rep":500,"min_level":7,"completed":False},
            # NEW MISSIONS
        # NEW MISSIONS - Extended gameplay
        {"id":"m9","title":"Darknet Kingpin","desc":"Become the most feared hacker",
         "target":"global","objectives":["Hack 5 players","Reach 500 reputation"],
         "reward_money":100000,"reward_xp":10000,"reward_rep":300,"min_level":6,"completed":False},
        {"id":"m10","title":"Faction War","desc":"Join a faction and reach rank 3",
         "target":"faction","objectives":["Join faction","Complete 3 faction tasks"],
         "reward_money":50000,"reward_xp":5000,"reward_rep":250,"min_level":5,"completed":False},
        {"id":"m11","title":"Tech Startup Breach","desc":"Infiltrate TechFlow startup",
         "target":"192.168.100.50","objectives":["Scan","Crack","Steal API keys"],
         "reward_money":1500,"reward_xp":200,"reward_rep":20,"min_level":2,"completed":False},
        {"id":"m12","title":"Healthcare Heist","desc":"Breach Hospital Network",
         "target":"10.1.1.1","objectives":["Bypass Firewall","Access MSSQL","Exfiltrate"],
         "reward_money":4000,"reward_xp":350,"reward_rep":40,"min_level":3,"completed":False},
        {"id":"m13","title":"Media Manipulation","desc":"Compromise news server",
         "target":"172.20.0.1","objectives":["Scan","Crack","Plant backdoor"],
         "reward_money":2500,"reward_xp":250,"reward_rep":30,"min_level":3,"completed":False},
        {"id":"m14","title":"Game Dev Raid","desc":"Steal from gaming studio",
         "target":"10.50.50.50","objectives":["Bypass FW","SQL inject","Download code"],
         "reward_money":3500,"reward_xp":400,"reward_rep":45,"min_level":4,"completed":False},
        {"id":"m15","title":"Crypto Heist 2.0","desc":"Rob CoinVault exchange",
         "target":"203.0.113.100","objectives":["Stealth hack","Bypass API","Steal funds"],
         "reward_money":20000,"reward_xp":1200,"reward_rep":120,"min_level":5,"completed":False},
        {"id":"m16","title":"E-commerce Takeover","desc":"Breach shopping platform",
         "target":"192.168.50.1","objectives":["Scan","Crack","Data mining"],
         "reward_money":3000,"reward_xp":300,"reward_rep":35,"min_level":3,"completed":False},
        {"id":"m17","title":"Research Espionage","desc":"Steal AI research data",
         "target":"10.75.75.75","objectives":["Advanced hack","Bypass FW","Exfiltrate"],
         "reward_money":6000,"reward_xp":700,"reward_rep":80,"min_level":4,"completed":False},
        {"id":"m18","title":"Legal Documents Theft","desc":"Rob law firm database",
         "target":"198.51.100.75","objectives":["RDP hack","MSSQL breach","Clean logs"],
         "reward_money":4500,"reward_xp":500,"reward_rep":60,"min_level":4,"completed":False},
        {"id":"m19","title":"Industrial Espionage","desc":"Compromise manufacturing plant",
         "target":"172.25.0.10","objectives":["Modbus attack","IoT breach","Control"],
         "reward_money":2000,"reward_xp":280,"reward_rep":25,"min_level":2,"completed":False},
        {"id":"m20","title":"Pharma Secrets","desc":"Steal pharmaceutical research",
         "target":"10.100.100.1","objectives":["Advanced FW bypass","Stealth hack","Exfiltrate"],
         "reward_money":12000,"reward_xp":1000,"reward_rep":150,"min_level":5,"completed":False},
        {"id":"m21","title":"Master Hacker","desc":"Compromise all targets",
         "target":"global","objectives":["Hack all 20 targets","Reach level 10"],
         "reward_money":250000,"reward_xp":50000,"reward_rep":1000,"min_level":8,"completed":False},
        {"id":"m22","title":"The Ultimate Heist","desc":"Steal from all major corporations",
         "target":"global","objectives":["Rob 5 corps","Earn $100k","Stay undetected"],
         "reward_money":150000,"reward_xp":20000,"reward_rep":500,"min_level":7,"completed":False},
    ]

def apply_save(self, completed):
    for m in self.missions:
        if m["id"] in completed:
            m["completed"] = True


# ============================================================
#                  NETWORK CLIENT
# ============================================================

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9999

class NetClient:
    def __init__(self):
        self.sock = None
        self.connected = False
        self.username = None
        self.online = False

    def connect(self, host, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)
            self.sock.connect((host, port))
            self.connected = True
            self.online = True
            return True
        except Exception as e:
            self.online = False
            return False

    def send(self, data):
        if not self.connected:
            return {"status": "error", "message": "Not connected"}
        try:
            msg = json.dumps(data) + "\n"
            self.sock.sendall(msg.encode('utf-8'))
            self.sock.settimeout(10)
            buf = ""
            while True:
                chunk = self.sock.recv(4096).decode('utf-8', errors='ignore')
                if not chunk:
                    self.connected = False
                    return {"status": "error", "message": "Disconnected"}
                buf += chunk
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        parsed = json.loads(line)
                        if parsed.get("type") in ("notification", "chat"):
                            continue
                        return parsed
                    except json.JSONDecodeError:
                        continue
        except socket.timeout:
            return {"status": "error", "message": "Timeout"}
        except Exception as e:
            self.connected = False
            return {"status": "error", "message": str(e)}

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass
        self.connected = False


# ============================================================
#                    MAIN GAME
# ============================================================

class HackStorm:
    def __init__(self):
        self.state = GameState()
        self.missions = MissionSystem()
        self.net = NetClient()
        self.history = []
        self.running = True
        self.save_counter = 0
        self.online_players = {}
        self.world_events = []

    # ── SYNC ──
    def sync_to_server(self):
        if not self.net.online:
            return
        try:
            self.net.send({
                "action": "save",
                "username": self.net.username,
                "game_state": self.state.to_dict(),
            })
        except Exception:
            pass

    def auto_sync(self):
        self.save_counter += 1
        if self.save_counter % 10 == 0:
            self.sync_to_server()

    # ── BOOT ──
    def boot(self):
        clear()
        matrix_rain(1.5)
        clear()
        gprint("  ================================================", (0,255,255), (0,100,255))
        gprint("         CYBER-OS v5.0.0 ENHANCED EDITION", (0,200,255), (100,255,200))
        gprint("  ================================================", (0,100,255), (0,255,255))
        print()
        for msg in ["Loading BIOS", "CPU: Quantum i9-X", "RAM: 32GB DDR6",
                     "Mounting filesystems", "Network daemon", "Crypto module AES-512",
                     "Hacking framework v5.0", "Loading faction database", "Initializing player tracker"]:
            type_loading(msg, random.uniform(0.2, 0.5))
        print()
        p(f"  {C.BOLD}{C.GREEN}[SYSTEM] All systems operational.{C.RESET}")
        print()
        print(easter_egg_text())
        print()
        time.sleep(1)
        clear()

    def show_banner(self):
        print()
        gprint("    ╦ ╦╔═╗╔═╗╦╔═╔═╗╔╦╗╔═╗╦═╗╔╦╗", (0,255,100), (0,200,255))
        gprint("    ╠═╣╠═╣║  ╠╩╗╚═╗ ║ ║ ║╠╦╝║║║", (0,200,255), (100,100,255))
        gprint("    ╩ ╩╩ ╩╚═╝╩ ╩╚═╝ ╩ ╚═╝╩╚═╩ ╩", (100,100,255), (200,0,255))
        mode = f"{C.GOLD}ONLINE{C.RESET}" if self.net.online else f"{C.STEEL}OFFLINE{C.RESET}"
        print(f"       {C.BOLD}{C.WHITE}Terminal Hacking Simulator PRO{C.RESET} [{mode}]")
        faction = f" | {self.state.faction_items.get(self.state.faction, {}).get('name', '')} [{self.state.faction_rank}]" if self.state.faction else ""
        gprint("  =============================================", (50,50,50), (150,150,150))
        p(f"   Type {C.GREEN}'help'{C.RESET} for commands | {C.GREEN}'tutorial'{C.RESET} to learn{faction}")
        gprint("  =============================================", (150,150,150), (50,50,50))
        print()

    def get_prompt(self):
        s = self.state
        net = s.current_network
        parts = []
        if s.vpn_active:
            parts.append(f"{C.GREEN}[VPN]{C.RESET}")
        if s.heat_level > 0:
            hc = C.GREEN if s.heat_level < 30 else (C.YELLOW if s.heat_level < 70 else C.RED)
            parts.append(f"{hc}[HEAT:{s.heat_level}%]{C.RESET}")
        if s.detection_level > 0:
            dc = C.GREEN if s.detection_level < 30 else (C.YELLOW if s.detection_level < 70 else C.RED)
            parts.append(f"{dc}[DET:{s.detection_level}%]{C.RESET}")
        if self.net.online:
            parts.append(f"{C.GOLD}[ON]{C.RESET}")
        extra = " ".join(parts)
        if extra:
            extra = " " + extra
        return f"{C.RED}{s.player_name}{C.RESET}@{C.CYAN}{net}{C.RESET}{extra} {C.GREEN}${C.RESET} "

    # ── TUTORIAL ──
    def cmd_tutorial(self, a):
        pages = [
            ("THE BASICS", [
                f"  {C.WHITE}You are a hacker. Complete missions, hack players, join factions.{C.RESET}",
                f"  {C.YELLOW}Commands:{C.RESET} help, status, missions, targets, shop, save",
            ]),
            ("HOW TO HACK", [
                f"  {C.CYAN}1.{C.RESET} {C.GREEN}nmap <ip>{C.RESET}            Scan ports",
                f"  {C.CYAN}2.{C.RESET} {C.GREEN}firewall_bypass <ip>{C.RESET}  Bypass firewall",
                f"  {C.CYAN}3.{C.RESET} {C.GREEN}crack <ip>{C.RESET}            Crack password",
                f"  {C.CYAN}4.{C.RESET} {C.GREEN}exploit <ip>{C.RESET}          Take over system",
                f"  {C.CYAN}5.{C.RESET} {C.GREEN}connect <ip>{C.RESET}          Access it",
                f"  {C.CYAN}6.{C.RESET} {C.GREEN}download <file>{C.RESET}       Steal files",
                f"  {C.CYAN}7.{C.RESET} {C.GREEN}clean_logs <ip>{C.RESET}       Cover tracks",
            ]),
            ("HACKING PLAYERS (NEW!)", [
                f"  {C.MAGENTA}hack_player <player>{C.RESET}     Attack another hacker",
                f"  {C.MAGENTA}steal_money <player> <amt>{C.RESET} Steal their cash",
                f"  {C.MAGENTA}plant_malware <player>{C.RESET}   Install backdoor",
                f"  {C.MAGENTA}track_player <player>{C.RESET}   Find their location",
                f"  {C.RED}Higher risk = Higher heat!{C.RESET}",
            ]),
            ("FACTIONS & HEAT", [
                f"  {C.CYAN}join_faction <faction>{C.RESET}    Join a group",
                f"  {C.CYAN}faction_quest{C.RESET}              Earn faction points",
                f"  {C.RED}Heat increases when you attack players{C.RESET}",
                f"  {C.GREEN}buy vpn{C.RESET}         - Reduce heat faster",
                f"  {C.GREEN}clean_logs{C.RESET}      - Drop heat 30%",
            ]),
            ("FIRST MISSION", [
                f"  Target: {C.WHITE}192.168.1.1{C.RESET} (Easy, no firewall)",
                f"  {C.CYAN}1.{C.RESET} buy hydra",
                f"  {C.CYAN}2.{C.RESET} nmap 192.168.1.1",
                f"  {C.CYAN}3.{C.RESET} crack 192.168.1.1",
                f"  {C.CYAN}4.{C.RESET} buy metasploit",
                f"  {{C.CYAN}5.{C.RESET} exploit 192.168.1.1",
                f"  {{C.CYAN}6.{C.RESET} connect 192.168.1.1",
                f"  {{C.CYAN}7.{C.RESET} download router_config.txt",
                f"  {C.CYAN}5.{C.RESET} exploit 192.168.1.1",
                f"  {C.CYAN}6.{C.RESET} connect 192.168.1.1",
                f"  {C.CYAN}7.{C.RESET} download router_config.txt",
            ]),
        ]
        for i, (title, lines) in enumerate(pages):
            clear()
            gprint(f"  === TUTORIAL ({i+1}/{len(pages)}) ===", (0,255,255), (100,100,255))
            neon_box(title, C.CYAN)
            print()
            for line in lines:
                print(line)
            print()
            if i < len(pages) - 1:
                input(f"  {C.DIM}[ENTER to continue]{C.RESET}")
            else:
                input(f"  {C.GREEN}[ENTER to start hacking!]{C.RESET}")
        self.state.tutorial_done = True
        clear()
        self.show_banner()

    # ── FACTION SYSTEM ──
    def cmd_factions(self, a):
        clear()
        print()
        gprint("  === FACTIONS ===", (200,0,200), (100,0,200))
        print()
        for fid, f in self.state.faction_items.items():
            status = f"{C.GREEN}[JOINED Rank {self.state.faction_rank}]{C.RESET}" if self.state.faction == fid else ""
            p(f"  {f['color']}{f['name']:<20}{C.RESET} {C.DIM}{f['desc']}{C.RESET} {status}")
        print()
        p(f"  Type {C.GREEN}'join_faction <name>'{C.RESET} to join")
        print()

    def cmd_join_faction(self, a):
        if not a:
            p("  [USAGE] join_faction <red_team|blue_team|ghost_net|syndicate>", C.YELLOW)
            return
        fid = a[0].lower()
        if fid not in self.state.faction_items:
            p("  [ERROR] Unknown faction.", C.RED)
            return
        if self.state.faction:
            p(f"  [ERROR] Already in {self.state.faction_items[self.state.faction]['name']}. Leave first.", C.RED)
            return
        self.state.faction = fid
        self.state.faction_rank = 1
        faction = self.state.faction_items[fid]
        clear()
        print()
        gprint(f"  === WELCOME TO {faction['name'].upper()} ===", tuple(map(ord, faction['color'])), (255, 100, 0))
        print(faction['color'] + C.BOLD + "=== WELCOME TO " + faction['name'].upper() + " ===" + C.RESET)
        print()
        p(f"  {C.BOLD}You have joined {faction['color']}{faction['name']}{C.RESET}")
        p(f"  {C.DIM}{faction['desc']}{C.RESET}")
        p(f"  {C.YELLOW}Bonus: {faction['bonus']}{C.RESET}")
        print()
        self.state.add_xp(50)
        self.state.reputation += 20

    def cmd_faction_quest(self, a):
        if not self.state.faction:
            p("  [ERROR] Join a faction first.", C.RED)
            return
        faction = self.state.faction_items[self.state.faction]
        clear()
        print()
        p(f"  {faction['color']}{C.BOLD}=== {faction['name']} QUEST ==={C.RESET}", faction['color'])
        print(faction['color'] + C.BOLD + f"=== {faction['name']} QUEST ===" + C.RESET)
        print()
        
        quests = {
            "red_team": [
                ("Sabotage Corporate Network", 5000, 200),
                ("DDoS rival faction", 3000, 150),
                ("Steal secret files", 4000, 180),
            ],
            "blue_team": [
                ("Defend against 5 attacks", 4000, 200),
                ("Patch critical vulnerabilities", 3500, 150),
                ("Find rogue hacker", 5000, 180),
            ],
            "ghost_net": [
                ("Complete 3 undetected hacks", 6000, 250),
                ("Gather intel on targets", 4000, 160),
                ("Stay hidden for 24hrs", 3000, 140),
            ],
            "syndicate": [
                ("Steal $50k from players", 5000, 220),
                ("Run extortion scheme", 4500, 190),
                ("Control 3 botnets", 6000, 200),
            ],
        }
        
        selected = random.choice(quests.get(self.state.faction, []))
        name, reward_xp, reward_rep = selected
        
        p(f"  {C.YELLOW}Quest: {name}{C.RESET}")
        p(f"  Difficulty: {C.ORANGE}{'*' * random.randint(2, 4)}{C.RESET}")
        p(f"  Reward: {C.CYAN}+{reward_xp} XP{C.RESET} {C.MAGENTA}+{reward_rep} Rep{C.RESET}")
        print()
        
        ch = input(f"  {C.GREEN}Accept? (y/n):{C.RESET} ").strip().lower()
        if ch == 'y':
            progress_bar("Completing quest", random.uniform(2, 4))
            self.state.add_xp(reward_xp)
            self.state.reputation += reward_rep
            self.state.faction_rank = min(5, self.state.faction_rank + 1)
            p(f"  {C.GREEN}Quest complete! Rank: {self.state.faction_rank}{C.RESET}")

    def cmd_create_faction(self, a):
        """Create a custom faction"""
        clear()
        print()
        gprint("  === CREATE FACTION ===", (255,100,255), (200,50,200))
        print()
        
        faction_name = input(f"  {C.GREEN}Faction Name:{C.RESET} ").strip()
        if not faction_name or len(faction_name) < 3:
            p(f"  {C.RED}Invalid name (min 3 chars){C.RESET}")
            return
        
        faction_desc = input(f"  {C.CYAN}Description:{C.RESET} ").strip()
        if not faction_desc:
            faction_desc = "A custom faction"
        
        faction_id = faction_name.lower().replace(" ", "_")
        if faction_id in self.state.faction_items or faction_id in self.state.custom_factions:
            p(f"  {C.RED}Faction name already exists!{C.RESET}")
            return
        
        # Cost to create faction
        creation_cost = 5000
        if self.state.money < creation_cost:
            p(f"  {C.RED}Need ${creation_cost:,} to create faction (you have ${self.state.money:,}){C.RESET}")
            return
        
        self.state.money -= creation_cost
        
        # Create the faction
        colors = [C.RED, C.BLUE, C.GREEN, C.MAGENTA, C.CYAN, C.YELLOW, C.ORANGE, C.PURPLE]
        chosen_color = random.choice(colors)
        
        self.state.custom_factions[faction_id] = {
            "name": faction_name,
            "desc": faction_desc,
            "color": chosen_color,
            "bonus": random.choice(["attack_power", "defense", "stealth", "money_steal"]),
            "creator": self.state.player_name,
            "members": [self.state.player_name],
            "level": 1
        }
        
        self.state.faction = faction_id
        self.state.faction_rank = 1
        
        clear()
        print()
        gprint("  === FACTION CREATED ===", chosen_color if chosen_color else C.CYAN, C.RESET)
        print()
        p(f"  {chosen_color}{C.BOLD}{faction_name}{C.RESET}")
        p(f"  {faction_desc}")
        p(f"  {C.YELLOW}Bonus: {self.state.custom_factions[faction_id]['bonus']}{C.RESET}")
        print()
        p(f"  {C.GREEN}✓ Faction created! Cost: ${creation_cost:,}{C.RESET}")
        p(f"  {C.CYAN}Invite friends with: 'invite_faction <player>'{C.RESET}")
        print()
        time.sleep(2)

    # ── PLAYER VS PLAYER ──
    def cmd_players(self, a):
        if not self.net.online:
            p("  [ERROR] Need to be online.", C.RED)
            return
        clear()
        print()
        gprint("  === ONLINE HACKERS ===", (255,100,0), (255,50,50))
        print()
        resp = self.net.send({"action": "get_players"})
        if resp.get("status") == "ok":
            players = resp.get("players", [])
            for player in players:
                if player["name"] == self.net.username:
                    continue
                threat = "LOW" if player["level"] < self.state.level else ("MEDIUM" if player["level"] == self.state.level else "HIGH")
                tc = C.GREEN if threat == "LOW" else (C.YELLOW if threat == "MEDIUM" else C.RED)
                p(f"  {C.CYAN}{player['name']:<16}{C.RESET} Lvl:{player['level']:<3} Rep:{player['reputation']:<6} [{tc}{threat}{C.RESET}]")
            print()
            p(f"  Type {C.GREEN}'hack_player <name>'{C.RESET} to attack")
        print()

    def cmd_hack_player(self, a):
        if not self.net.online:
            p("  [ERROR] Need to be online.", C.RED)
            return
        if not a:
            p("  [USAGE] hack_player <player_name>", C.YELLOW)
            return
        
        target_name = a[0]
        if target_name == self.net.username:
            p("  [ERROR] Can't hack yourself, genius.", C.RED)
            return
        
        self.state.hacks_attempted += 1
        self.state.increase_detection(20)
        self.state.heat_level = min(100, self.state.heat_level + 30)
        
        clear()
        print()
        glitch_text(f"  PLAYER EXPLOIT - {target_name}")
        print()
        
        resp = self.net.send({"action": "get_player_info", "target": target_name})
        if resp.get("status") != "ok":
            epic_fail("Target not found or offline!")
            return
        
        target = resp.get("player", {})
        target_level = target.get("level", 1)
        
        # Success chance based on levels
        base_chance = 50
        if self.state.level > target_level:
            base_chance += (self.state.level - target_level) * 10
        else:
            base_chance -= (target_level - self.state.level) * 10
        
        # VPN bonus
        if self.state.vpn_active:
            base_chance += 15
        
        # Firewall defense for target
        if "firewall_upgrade" in target.get("tools", []):
            base_chance -= 20
        
        base_chance = max(10, min(90, base_chance))
        
        hacker_bar("Breaching defenses...", 3)
        
        if random.randint(1, 100) <= base_chance:
            self.state.hacks_successful += 1
            self.state.players_hacked.append(target_name)
            
            # Steal money
            steal_amount = random.randint(100, min(500, target.get("money", 0) // 2))
            self.state.money += steal_amount
            
            print()
            p(f"  {C.BG_DARK_GREEN}{C.WHITE}{C.BOLD} HACK SUCCESSFUL! {C.RESET}")
            p(f"  {C.GREEN}Stole ${steal_amount:,} from {target_name}{C.RESET}")
            p(f"  {C.CYAN}+50 XP{C.RESET}")
            self.state.add_xp(50)
            self.state.reputation += 30
            
            # Notify victim
            self.net.send({
                "action": "notify",
                "target": target_name,
                "message": f"{self.net.username} hacked you and stole ${steal_amount:,}!"
            })
        else:
            print()
            p(f"  {C.BG_DARK_RED}{C.WHITE}{C.BOLD} HACK FAILED! {C.RESET}")
            p(f"  {C.RED}Their defenses were too strong.{C.RESET}")
            self.state.increase_detection(15)
            self.state.heat_level = min(100, self.state.heat_level + 20)
            
            # Target might trace you
            if random.randint(1, 100) <= 30:
                p(f"  {C.YELLOW}WARNING: Target is tracing you!{C.RESET}")
                self.state.increase_detection(10)
        
        print()

    def cmd_track_player(self, a):
        if "player_tracker" not in self.state.tools:
            p("  [ERROR] player_tracker tool needed.", C.RED)
            return
        if not a:
            p("  [USAGE] track_player <name>", C.YELLOW)
            return
        
        if not self.net.online:
            p("  [ERROR] Need to be online.", C.RED)
            return
        
        print()
        type_loading(f"Tracking {a[0]}", 2)
        type_loading("Triangulating signal", 1.5)
        
        resp = self.net.send({"action": "get_player_info", "target": a[0]})
        if resp.get("status") == "ok":
            target = resp.get("player", {})
            print()
            p(f"  {C.GREEN}Target located:{C.RESET}")
            p(f"    Name: {target.get('name', '?')}")
            p(f"    Level: {target.get('level', '?')}")
            p(f"    Money: ${target.get('money', 0):,}")
            p(f"    Location: {random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}")
            print()
        else:
            p(f"  {C.RED}Target not found.{C.RESET}")

    # ── ORIGINAL COMMANDS ──
    def cmd_help(self, a):
        clear()
        cats = {
            "GENERAL": {"help":"Commands","status":"Stats","clear":"Clear","missions":"Missions",
                "shop":"Shop","buy <x>":"Purchase","inventory":"Items","targets":"Targets",
                "tutorial":"Tutorial","save":"Save","whoami":"Identity","time":"Time",
                "history":"History","note <x>":"Save note","notes":"View notes",
                "crypto":"Wallet","leaderboard":"Rankings","exit":"Quit"},
            "NETWORK": {"nmap <ip>":"Scan","ping <ip>":"Ping","connect <ip>":"Connect",
                "disconnect":"Disconnect","traceroute <ip>":"Trace","netmap":"Map",
                "whois <ip>":"Lookup","dns <x>":"DNS"},
            "HACKING": {"crack <ip>":"Crack pw","exploit <ip>":"Exploit","sqlinject <ip>":"SQLi",
                "sniff":"Sniff traffic","bruteforce <ip>":"Brute-force",
                "firewall_bypass <ip>":"Bypass FW","phish <ip>":"Phish",
                "ddos <ip>":"DDoS","wifihack":"WiFi crack","ransomware <ip>":"Ransomware",
                "keylog <ip>":"Keylogger"},
            "POST-EXPLOIT": {"download <f>":"Download","backdoor <ip>":"Backdoor",
                "clean_logs <ip>":"Clean logs","cat <f>":"Read file","mine <ip>":"Mine crypto",
                "analyze <f>":"Forensics","pivot <ip>":"Pivot network"},
            "DEFENSE": {"vpn":"Toggle VPN","proxy":"Proxy status","encrypt <f>":"Encrypt",
                "shred <f>":"Destroy file","spoof":"Spoof MAC"},
            "PLAYER VS PLAYER": {"players":"List online","hack_player <x>":"Attack player",
                "track_player <x>":"Find player","profile <x>":"Player profile"},
            "FACTIONS": {"factions":"List factions","join_faction <x>":"Join group",
                "faction_quest":"Take quest"},
        }
        if self.net.online:
            cats["ONLINE"] = {"online":"Who's online","chat <msg>":"Chat","chatlog":"Chat history",
                "serverinfo":"Server info"}

        print()
        gprint("  === COMMAND REFERENCE ===", (0,255,255), (100,100,255))
        cc = {"GENERAL":C.GREEN,"NETWORK":C.CYAN,"HACKING":C.RED,"POST-EXPLOIT":C.ORANGE,"DEFENSE":C.BLUE,"PLAYER VS PLAYER":C.MAGENTA,"FACTIONS":C.PURPLE,"ONLINE":C.GOLD}
        for cat, cmds in cats.items():
            print()
            p(f"  {cc.get(cat,C.YELLOW)}{C.BOLD}-- {cat} --{C.RESET}")
            for cmd, desc in cmds.items():
                p(f"    {C.WHITE}{cmd:<25}{C.RESET}{C.DIM}{desc}{C.RESET}")
        print()

    def cmd_status(self, a):
        clear()
        s = self.state
        print()
        gprint("  === HACKER PROFILE ===", (0,255,200), (0,150,255))
        print()
        p(f"    {C.STEEL}Alias:{C.RESET}       {C.BOLD}{C.CYAN}{s.player_name}{C.RESET}")
        p(f"    {C.STEEL}IP:{C.RESET}          {C.GREEN}{s.ip_address}{C.RESET}")
        p(f"    {C.STEEL}Level:{C.RESET}       {C.GOLD}{C.BOLD}{s.level}{C.RESET}")
        xp_pct = s.xp / max(s.xp_to_next, 1)
        filled = int(xp_pct * 20)
        p(f"    {C.STEEL}XP:{C.RESET}          [{C.CYAN}{'#'*filled}{C.STEEL}{'-'*(20-filled)}{C.RESET}] {s.xp}/{s.xp_to_next}")
        p(f"    {C.STEEL}Money:{C.RESET}       {C.GOLD}${s.money:,}{C.RESET}")
        p(f"    {C.STEEL}Crypto:{C.RESET}      {C.ORANGE}{s.crypto_wallet:.6f} BTC{C.RESET}")
        p(f"    {C.STEEL}Reputation:{C.RESET}  {C.MAGENTA}{s.reputation}{C.RESET}")
        faction_info = f" [{self.state.faction_items[s.faction]['color']}{self.state.faction_items[s.faction]['name']}{C.RESET}]" if s.faction else ""
        p(f"    {C.STEEL}Faction:{C.RESET}     {faction_info}")
        vc = C.GREEN if s.vpn_active else C.RED
        p(f"    {C.STEEL}VPN:{C.RESET}         {vc}{'ON' if s.vpn_active else 'OFF'}{C.RESET}")
        p(f"    {C.STEEL}Proxies:{C.RESET}     {C.BLUE}{s.proxy_chains}{C.RESET}")
        p(f"    {C.STEEL}Botnet:{C.RESET}      {C.PURPLE}{s.botnet_size}{C.RESET}")
        det = s.detection_level
        dc = C.GREEN if det < 30 else (C.YELLOW if det < 70 else C.RED)
        dl = "LOW" if det < 30 else ("MED" if det < 70 else "CRIT!")
        df = int((det/100)*20)
        p(f"    {C.STEEL}Detection:{C.RESET}   [{dc}{'#'*df}{C.STEEL}{'-'*(20-df)}{C.RESET}] {dc}{det}% ({dl}){C.RESET}")
        heat = s.heat_level
        hc = C.GREEN if heat < 30 else (C.YELLOW if heat < 70 else C.RED)
        hf = int((heat/100)*20)
        p(f"    {C.STEEL}Heat:{C.RESET}        [{hc}{'#'*hf}{C.STEEL}{'-'*(20-hf)}{C.RESET}] {hc}{heat}%{C.RESET}")
        p(f"    {C.STEEL}Hacks:{C.RESET}       {C.RED}{s.hacks_successful}/{s.hacks_attempted}{C.RESET}")
        p(f"    {C.STEEL}Network:{C.RESET}     {C.CYAN}{s.current_network}{C.RESET}")
        if s.connected_to:
            p(f"    {C.STEEL}Connected:{C.RESET}   {C.GREEN}{s.connected_to}{C.RESET}")
        comp = len([m for m in self.missions.missions if m['completed']])
        p(f"    {C.STEEL}Missions:{C.RESET}    {comp}/{len(self.missions.missions)}")
        p(f"    {C.STEEL}Mode:{C.RESET}        {C.GOLD}{'ONLINE' if self.net.online else 'OFFLINE'}{C.RESET}")
        print()

    def cmd_targets(self, a):
        clear()
        print()
        gprint("  === KNOWN TARGETS ===", (255,100,100), (255,50,50))
        print()
        for ip, t in self.state.available_targets.items():
            st = f"{C.GREEN}[HACKED]{C.RESET}" if t["compromised"] else f"{C.RED}[SECURED]{C.RESET}"
            ic = C.GREEN if t["compromised"] else C.RED
            diff = f"{C.GOLD}{'*'*t['difficulty']}{'.'*(5-t['difficulty'])}{C.RESET}"
            p(f"    {C.BOLD}{ic}{ip:<18}{C.RESET} {C.WHITE}{t['name']}{C.RESET}")
            fw = f"{C.YELLOW}Lvl {t.get('firewall_level',0)}{C.RESET}" if t['firewall'] else f"{C.GREEN}No{C.RESET}"
            p(f"      {C.STEEL}OS:{C.RESET} {t['os']}  {diff}  {st}  {C.STEEL}FW:{C.RESET} {fw}")
            print()

    def cmd_nmap(self, a):
        if "nmap" not in self.state.tools: p("  [ERROR] nmap not installed.", C.RED); return
        if not a: p("  [USAGE] nmap <ip>", C.YELLOW); return
        ip = a[0]
        if ip not in self.state.available_targets: p(f"  [ERROR] Host {ip} not found.", C.RED); return
        clear(); t = self.state.available_targets[ip]; self.state.increase_detection(5)
        print(); glitch_text(f"  NMAP SCAN - {ip}"); print()
        scan_anim(ip, 3); print()
        p(f"  {C.BOLD}{C.WHITE}Nmap report: {ip}{C.RESET}")
        p(f"  {C.DIM}Host up | OS: {t['os']}{C.RESET}"); print()
        p(f"  {C.BOLD}{'PORT':<12}{'STATE':<10}{'SERVICE'}{C.RESET}")
        gprint(f"  {'='*35}", (100,100,100), (50,50,50))
        for port, svc in t['ports'].items():
            time.sleep(0.3)
            p(f"  {C.CYAN}{str(port)+'/tcp':<12}{C.GREEN}{'open':<10}{C.WHITE}{svc}{C.RESET}")
        print()
        if t['firewall']:
            p(f"  {C.BG_DARK_RED}{C.YELLOW}{C.BOLD} FIREWALL DETECTED (Level {t.get('firewall_level',1)}) {C.RESET}")
        else:
            p(f"  {C.GREEN}No firewall{C.RESET}")
        print()

    def cmd_ping(self, a):
        if not a: p("  [USAGE] ping <ip>", C.YELLOW); return
        ip = a[0]; print()
        for _ in range(4):
            ms = random.uniform(0.5, 50.0)
            if ip in self.state.available_targets:
                p(f"  {C.GREEN}Reply from {ip}: time={ms:.1f}ms{C.RESET}")
            else:
                p(f"  {C.RED}Request timed out.{C.RESET}")
            time.sleep(0.4)
        print()

    def cmd_traceroute(self, a):
        if not a: p("  [USAGE] traceroute <ip>", C.YELLOW); return
        clear(); print(); glitch_text(f"  TRACEROUTE - {a[0]}"); print()
        for i in range(1, random.randint(5, 12)):
            ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            p(f"  {C.CYAN}{i:>3}{C.RESET}  {random.uniform(1,100):>7.2f} ms  {ip}")
            time.sleep(0.2)
        print()

    def cmd_connect(self, a):
        if not a: p("  [USAGE] connect <ip>", C.YELLOW); return
        ip = a[0]
        if ip not in self.state.available_targets: p(f"  [ERROR] Unknown.", C.RED); return
        t = self.state.available_targets[ip]
        if not t["compromised"]:
            p(f"  {C.BG_DARK_RED}{C.WHITE}{C.BOLD} ACCESS DENIED {C.RESET}"); return
        type_loading(f"Connecting to {ip}", 1.5)
        self.state.connected_to = ip
        self.state.current_network = t["name"].replace(" ","_").lower()
        p(f"  {C.BG_DARK_GREEN}{C.WHITE}{C.BOLD} ACCESS GRANTED {C.RESET}")
        p(f"  {C.GREEN}{t['name']} | {t['os']}{C.RESET}")

    def cmd_disconnect(self, a):
        if not self.state.connected_to: p("  Not connected.", C.YELLOW); return
        p(f"  {C.GREEN}Disconnected from {self.state.connected_to}{C.RESET}")
        self.state.connected_to = None; self.state.current_network = "home"

    def cmd_crack(self, a):
        if "hydra" not in self.state.tools and "john" not in self.state.tools:
            p("  [ERROR] Need hydra or john.", C.RED); return
        if not a: p("  [USAGE] crack <ip>", C.YELLOW); return
        ip = a[0]
        if ip not in self.state.available_targets: p(f"  [ERROR] Unknown.", C.RED); return
        t = self.state.available_targets[ip]
        if t["firewall"] and not self.state.firewall_bypassed:
            p("  [ERROR] Firewall blocking!", C.RED); self.state.increase_detection(15); return
        clear(); self.state.increase_detection(10)
        print(); glitch_text(f"  PASSWORD CRACKER - {ip}"); print()
        tool = "Hydra" if "hydra" in self.state.tools else "John"
        p(f"  {C.CYAN}Tool: {tool} | Wordlist: rockyou.txt{C.RESET}"); print()
        hacker_bar("Cracking hash...", random.uniform(2, 4)); fake_data(5)
        diff = t["difficulty"]
        chance = max(20, 90 - diff*15 + self.state.level*10)
        if "john" in self.state.tools and "hydra" in self.state.tools: chance += 15
        if random.randint(1, 100) <= chance:
            pw = t["password"]; self.state.known_passwords[ip] = pw
            print(); pw_crack_anim(pw, 2); print()
            neon_box(f"CRACKED: {pw}", C.GREEN)
        else:
            print(); p("  [FAIL] Too complex. Level up or buy better tools.", C.RED)
        print()

    def cmd_firewall_bypass(self, a):
        if not a: p("  [USAGE] firewall_bypass <ip>", C.YELLOW); return
        ip = a[0]
        if ip not in self.state.available_targets: p("  [ERROR] Unknown.", C.RED); return
        t = self.state.available_targets[ip]
        if not t["firewall"]: p("  No firewall here.", C.YELLOW); return
        clear(); fw = t.get("firewall_level", 1); self.state.increase_detection(10 + fw*5)
        print(); glitch_text(f"  FIREWALL BYPASS - {ip}"); print()
        p(f"  {C.RED}{'#'*40}{C.RESET}")
        p(f"  {C.RED}#{C.RESET} {C.BOLD}FIREWALL Level {fw}{C.RESET}             {C.RED}#{C.RESET}")
        p(f"  {C.RED}{'#'*40}{C.RESET}"); print()
        type_loading("Probing rules", 1.5); type_loading("Finding vulns", 2)
        if "zero_day" in self.state.tools:
            p(f"  {C.NEON_PINK}{C.BOLD}Deploying ZERO-DAY...{C.RESET}")
            hacker_bar("Bypassing...", 1.5)
            p(f"  {C.BG_DARK_GREEN}{C.WHITE}{C.BOLD} BYPASSED (zero-day) {C.RESET}")
            self.state.firewall_bypassed = True; return
        chance = max(10, 80 - fw*15 + self.state.level*8)
        if "metasploit" in self.state.tools: chance += 20
        hacker_bar("Attempting bypass...", 3)
        if random.randint(1, 100) <= chance:
            self.state.firewall_bypassed = True
            p(f"\n  {C.BG_DARK_GREEN}{C.WHITE}{C.BOLD} FIREWALL BYPASSED! {C.RESET}")
        else:
            p(f"\n  {C.RED}[FAIL] Too strong.{C.RESET}"); self.state.increase_detection(10)
        print()

    def cmd_exploit(self, a):
        if "metasploit" not in self.state.tools: p("  [ERROR] Need metasploit.", C.RED); return
        if not a: p("  [USAGE] exploit <ip>", C.YELLOW); return
        ip = a[0]
        if ip not in self.state.available_targets: p("  [ERROR] Unknown.", C.RED); return
        t = self.state.available_targets[ip]
        if t["compromised"]: p("  Already hacked.", C.YELLOW); return
        if ip not in self.state.known_passwords: p("  [ERROR] Crack password first.", C.RED); return
        if t["firewall"] and not self.state.firewall_bypassed: p("  [ERROR] Firewall active!", C.RED); return
        clear(); self.state.increase_detection(15)
        print(); glitch_text(f"  EXPLOIT LAUNCHER - {ip}"); print()
        exploits = ["ms17_010_eternalblue","vsftpd_234_backdoor","libssh_auth_bypass","apache_struts_rce"]
        p(f"  {C.CYAN}Exploit:{C.RESET}  {random.choice(exploits)}")
        p(f"  {C.CYAN}Payload:{C.RESET}  meterpreter/reverse_tcp")
        p(f"  {C.CYAN}LHOST:{C.RESET}    {self.state.ip_address}"); print()
        type_loading("Sending exploit", 1.5); hacker_bar("Executing payload...", 2); fake_data(8)
        chance = max(30, 85 - t["difficulty"]*10 + self.state.level*10)
        if random.randint(1, 100) <= chance:
            t["compromised"] = True; self.state.firewall_bypassed = False
            print(); p(f"  {C.BG_DARK_GREEN}{C.WHITE}{C.BOLD} SYSTEM COMPROMISED! {C.RESET}")
            loot = t["loot"]; self.state.money += loot["money"]; self.state.add_xp(loot["xp"])
            for f in loot["files"]:
                if f not in self.state.files: self.state.files.append(f)
            p(f"  {C.GOLD}+${loot['money']:,}{C.RESET}  {C.CYAN}+{loot['xp']} XP{C.RESET}")
            p(f"  {C.GREEN}Files: {', '.join(loot['files'])}{C.RESET}")
            self._check_missions(ip)
        else:
            print(); p(f"  {C.BG_DARK_RED}{C.WHITE}{C.BOLD} EXPLOIT FAILED {C.RESET}")
            self.state.increase_detection(20)
        print()

    def cmd_sqlinject(self, a):
        if "sqlmap" not in self.state.tools: p("  [ERROR] sqlmap needed.", C.RED); return
        if not a: p("  [USAGE] sqlinject <ip>", C.YELLOW); return
        ip = a[0]
        if ip not in self.state.available_targets: p("  [ERROR] Unknown.", C.RED); return
        t = self.state.available_targets[ip]
        if not any(s in ["MySQL","PostgreSQL","MSSQL"] for s in t.get("services",[])): p("  [ERROR] No DB.", C.RED); return
        clear(); self.state.increase_detection(10)
        print(); glitch_text(f"  SQL INJECTION - {ip}"); print()
        for pl in ["' OR 1=1 --","' UNION SELECT * --","'; DROP TABLE users; --"]:
            typing_anim(pl, 0.02); time.sleep(0.2)
        hacker_bar("Exploiting...", 2)
        if random.randint(1, 100) <= 70 + self.state.level*5:
            print(); p(f"  {C.BG_DARK_GREEN}{C.WHITE}{C.BOLD} SQL INJECTION SUCCESS {C.RESET}"); print()
            for t_name in ["users","accounts","transactions"]:
                p(f"  {C.GREEN}{t_name:<20}{random.randint(100,50000)} rows{C.RESET}"); time.sleep(0.2)
            self.state.add_xp(50); self.state.money += 200
        else:
            p(f"  {C.RED}[FAIL] No injectable params.{C.RESET}")
        print()

    def cmd_sniff(self, a):
        if "wireshark" not in self.state.tools: p("  [ERROR] Wireshark needed.", C.RED); return
        clear(); print(); glitch_text("  PACKET SNIFFER"); print()
        protos = ["TCP","UDP","HTTP","HTTPS","DNS","FTP","SSH"]
        pc = {"TCP":C.CYAN,"UDP":C.BLUE,"HTTP":C.GREEN,"HTTPS":C.LIME,"DNS":C.YELLOW,"FTP":C.ORANGE,"SSH":C.MAGENTA}
        for i in range(20):
            src = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            dst = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            pr = random.choice(protos)
            p(f"  {C.DIM}{i+1:>4}{C.RESET}  {src} {C.STEEL}->{C.RESET} {dst}  {pc.get(pr,C.WHITE)}{pr:<6}{C.RESET} {random.randint(40,1500)}B")
            time.sleep(0.1)
            if random.randint(1,12)==1:
                u = random.choice(["admin","root","user"]); pw = random.choice(["letmein","pass123","qwerty"])
                p(f"        {C.BG_DARK_RED}{C.WHITE} INTERCEPTED: {u}:{pw} {C.RESET}")
                self.state.intercepted_data.append(f"{u}:{pw}")
        print(); p(f"  {C.GREEN}Done. {len(self.state.intercepted_data)} credentials captured.{C.RESET}")
        self.state.add_xp(25); print()

    def cmd_bruteforce(self, a):
        if "hydra" not in self.state.tools: p("  [ERROR] Hydra needed.", C.RED); return
        if not a: p("  [USAGE] bruteforce <ip>", C.YELLOW); return
        clear(); self.state.increase_detection(20)
        print(); glitch_text(f"  BRUTE FORCE - {a[0]}")
        p(f"  {C.BG_DARK_RED}{C.WHITE} HIGH DETECTION RISK {C.RESET}"); print()
        att = random.randint(500, 5000)
        for i in range(0, att, att//20):
            pw = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=random.randint(6,12)))
            sys.stdout.write(f"\r  {C.YELLOW}[{i}/{att}]{C.RESET} {C.DIM}{pw}{C.RESET}          ")
            sys.stdout.flush(); time.sleep(0.08)
        ip = a[0]
        if ip in self.state.available_targets:
            pw = self.state.available_targets[ip]["password"]
            print("\n"); pw_crack_anim(pw, 2); neon_box(f"Password: {pw}", C.GREEN)
            self.state.known_passwords[ip] = pw
        else:
            print(f"\n\n  {C.RED}[FAIL]{C.RESET}")
        print()

    def cmd_download(self, a):
        if not self.state.connected_to: p("  [ERROR] Connect first.", C.RED); return
        if not a: p("  [USAGE] download <file>", C.YELLOW); return
        t = self.state.available_targets[self.state.connected_to]
        avail = t["loot"]["files"]
        if a[0] not in avail: p(f"  [ERROR] Not found. Available: {', '.join(avail)}", C.RED); return
        hacker_bar(f"Downloading {a[0]}...", random.uniform(1.5, 3))
        if a[0] not in self.state.files: self.state.files.append(a[0])
        p(f"  {C.GREEN}Downloaded {a[0]}{C.RESET}")
        self.state.increase_detection(5); self.state.add_xp(20)

    def cmd_backdoor(self, a):
        if "rootkit" not in self.state.tools: p("  [ERROR] Rootkit needed.", C.RED); return
        if not a: p("  [USAGE] backdoor <ip>", C.YELLOW); return
        ip = a[0]
        if ip not in self.state.available_targets or not self.state.available_targets[ip]["compromised"]:
            p("  [ERROR] Not compromised.", C.RED); return
        type_loading("Deploying rootkit", 2); type_loading("Hiding processes", 1)
        self.state.backdoors.append(ip)
        p(f"  {C.GREEN}Backdoor on {ip} (port 31337){C.RESET}"); self.state.add_xp(40)

    def cmd_clean_logs(self, a):
        if not a: p("  [USAGE] clean_logs <ip>", C.YELLOW); return
        ip = a[0]
        if ip not in self.state.available_targets or not self.state.available_targets[ip]["compromised"]:
            p("  [ERROR] No access.", C.RED); return
        clear(); print(); glitch_text(f"  LOG CLEANER - {ip}"); print()
        for log in ["/var/log/auth.log","/var/log/syslog","/var/log/access.log","/var/log/secure"]:
            type_loading(f"Wiping {log}", random.uniform(0.2,0.5))
        self.state.log_cleaned.append(ip)
        self.state.detection_level = max(0, self.state.detection_level - 30)
        self.state.heat_level = max(0, self.state.heat_level - 20)
        p(f"\n  {C.GREEN}Logs cleaned! Detection -30%, Heat -20%{C.RESET}"); self.state.add_xp(30)

    def cmd_cat(self, a):
        if not a: p("  [USAGE] cat <file>", C.YELLOW); return
        if a[0] not in self.state.files: p(f"  [ERROR] Not found.", C.RED); return
        contents = {
            "readme.txt":"Welcome to CyberOS. Type 'help'.",
            "notes.txt":"TODO: Upgrade tools, complete missions, don't get caught!",
            "router_config.txt":"SSID=HomeNetwork\nWPA2=mysecretkey123\nADMIN=admin123",
            "customer_db.sql":"-- 15,342 records (names, emails, credit cards)",
            "emails.txt":"From: ceo@business.com\nPassword is still P@ssw0rd...",
            "student_records.db":"-- 45,000 students (names, SSNs, grades)",
            "research_data.zip":"[Encrypted - 147 research papers]",
            "financial_reports.xlsx":"Q1: $45M | Q2: $52M | Profit: $12.5M",
            "employee_data.csv":"John Smith,CEO,$500k | 2,847 records...",
            "trade_secrets.doc":"[CLASSIFIED] Project Nexus: AI market manipulation",
            "classified_intel.enc":"[TOP SECRET - AES-256]",
            "agent_list.gpg":"[PGP - 200+ agents - LIVES AT RISK]",
            "operation_files.tar.gz":"[Missions, surveillance - 890 MB]",
            "transaction_logs.db":"TXN: $50k->Offshore | $1M->[REDACTED]",
            "account_data.enc":"[500k accounts - $2.8B assets]",
            "market_users.db":"-- 25k dark web accounts + BTC wallets",
            "crypto_wallets.dat":"BTC: 142.5 | ETH: 3,500 | ~$8.5M",
            "sat_telemetry.dat":"Orbit: LEO 400km | Freq: 2.4GHz",
            "comm_encryption.key":"-----BEGIN RSA PRIVATE KEY-----",
            "orbital_data.bin":"[TLE data for 200+ satellites]",
        }
        content = contents.get(a[0], f"[{a[0]}]")
        print(); gprint(f"  --- {a[0]} ---", (100,200,255), (50,100,200))
        for line in content.split('\n'):
            decrypt_anim(line, 0.02)
        gprint(f"  --- EOF ---", (50,100,200), (100,200,255)); print()

    def cmd_inventory(self, a):
        clear(); print(); gprint("  === INVENTORY ===", (255,200,0), (255,100,0)); print()
        p(f"  {C.BOLD}{C.ORANGE}TOOLS{C.RESET}")
        for t in self.state.tools: p(f"    {C.GREEN}+{C.RESET} {t}")
        print(); p(f"  {C.BOLD}{C.CYAN}FILES{C.RESET}")
        for f in self.state.files: p(f"    {C.BLUE}>{C.RESET} {f}")
        if self.state.backdoors:
            print(); p(f"  {C.BOLD}{C.RED}BACKDOORS{C.RESET}")
            for b in self.state.backdoors: p(f"    {C.RED}!{C.RESET} {b}")
        if self.state.known_passwords:
            print(); p(f"  {C.BOLD}{C.MAGENTA}PASSWORDS{C.RESET}")
            for ip, pw in self.state.known_passwords.items(): p(f"    {C.MAGENTA}@{C.RESET} {ip}: {C.GREEN}{pw}{C.RESET}")
        if self.state.intercepted_data:
            print(); p(f"  {C.BOLD}{C.YELLOW}INTERCEPTED{C.RESET}")
            for d in self.state.intercepted_data: p(f"    {C.YELLOW}~{C.RESET} {d}")
        if self.state.players_hacked:
            print(); p(f"  {C.BOLD}{C.NEON_PINK}COMPROMISED PLAYERS{C.RESET}")
            for pl in self.state.players_hacked: p(f"    {C.NEON_PINK}◆{C.RESET} {pl}")
        print()

    def cmd_shop(self, a):
        clear(); print(); gprint("  === BLACK MARKET ===", (200,0,255), (100,0,200))
        fire_text("        * BLACK MARKET SHOP *")
        p(f"\n  {C.GOLD}Balance: ${self.state.money:,}{C.RESET}\n")
        tc = {"tool":C.RED,"service":C.CYAN,"upgrade":C.YELLOW}
        for item_id, item in self.state.shop_items.items():
            owned = item_id in self.state.tools
            if item_id == "vpn": owned = self.state.vpn_active
            status = f"{C.DIM}[OWNED]{C.RESET}" if owned else ""
            if item_id == "proxy_chain": status = f"{C.DIM}[x{self.state.proxy_chains}]{C.RESET}"
            elif item_id == "botnet_node": status = f"{C.DIM}[{self.state.botnet_size}]{C.RESET}"
            ic = tc.get(item["type"], C.WHITE)
            p(f"    {ic}{item_id:<18}{C.RESET}{C.GOLD}${item['price']:<8}{C.RESET}{C.DIM}{item['desc']}{C.RESET} {status}")
        p(f"\n  Type {C.GREEN}buy <item>{C.RESET} to purchase."); print()

    def cmd_buy(self, a):
        if not a: p("  [USAGE] buy <item>", C.YELLOW); return
        item_id = a[0].lower()
        if item_id not in self.state.shop_items: p(f"  [ERROR] Unknown '{item_id}'.", C.RED); return
        item = self.state.shop_items[item_id]
        if item["type"] == "tool" and item_id in self.state.tools: p("  Already owned.", C.YELLOW); return
        if self.state.money < item["price"]: p(f"  [ERROR] Need ${item['price']:,}, have ${self.state.money:,}.", C.RED); return
        self.state.money -= item["price"]
        if item["type"] == "tool": self.state.tools.append(item_id); p(f"  {C.GREEN}Purchased {item_id}!{C.RESET}")
        elif item_id == "vpn": self.state.vpn_active = True; p(f"  {C.GREEN}VPN activated!{C.RESET}")
        elif item_id == "proxy_chain": self.state.proxy_chains += 1; p(f"  {C.GREEN}Proxy +1 ({self.state.proxy_chains}){C.RESET}")
        elif item_id == "botnet_node": self.state.botnet_size += 10; p(f"  {C.GREEN}+10 bots ({self.state.botnet_size}){C.RESET}")
        else: p(f"  {C.GREEN}Purchased!{C.RESET}")
        p(f"  {C.GOLD}Balance: ${self.state.money:,}{C.RESET}")

    def cmd_missions(self, a):
        clear(); print(); gprint("  === MISSION BOARD ===", (255,215,0), (255,140,0)); print()
        for m in self.missions.missions:
            if m["completed"]: st = f"{C.GREEN}[DONE]{C.RESET}"; tc = C.DIM
            elif m["min_level"] > self.state.level: st = f"{C.RED}[LOCKED Lvl {m['min_level']}]{C.RESET}"; tc = C.DIM
            else: st = f"{C.YELLOW}[AVAILABLE]{C.RESET}"; tc = C.BOLD + C.WHITE
            p(f"  {tc}{m['title']}{C.RESET}  {st}")
            p(f"    {C.DIM}{m['desc']}{C.RESET}")
            p(f"    {C.STEEL}Target:{C.RESET} {m['target']}  {C.GOLD}${m['reward_money']:,}{C.RESET} + {C.CYAN}{m['reward_xp']} XP{C.RESET}")
            for o in m["objectives"]: p(f"      {C.STEEL}-{C.RESET} {o}")
            print()

    def cmd_vpn(self, a):
        if self.state.vpn_active:
            self.state.vpn_active = False; p(f"  {C.RED}VPN OFF. IP exposed!{C.RESET}")
        else:
            self.state.vpn_active = True
            p(f"  {C.GREEN}VPN ON! IP: {random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}{C.RESET}")

    def cmd_proxy(self, a):
        print(); p(f"  {C.BOLD}Proxies: {self.state.proxy_chains}{C.RESET}")
        countries = ["Romania","Russia","Brazil","Japan","Sweden","Iceland","Panama"]
        for i in range(self.state.proxy_chains):
            p(f"    {C.CYAN}Chain {i+1}:{C.RESET} {random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)} ({random.choice(countries)})")
        if not self.state.proxy_chains: p("  None. Buy from shop.", C.DIM)
        print()

    def cmd_encrypt(self, a):
        if not a or a[0] not in self.state.files: p("  [ERROR] File not found.", C.RED); return
        type_loading(f"Encrypting {a[0]} (AES-256)", 1.5); p(f"  {C.GREEN}Encrypted.{C.RESET}"); self.state.add_xp(5)

    def cmd_shred(self, a):
        if not a or a[0] not in self.state.files: p("  [ERROR] File not found.", C.RED); return
        type_loading(f"Shredding {a[0]} (35-pass)", 2); self.state.files.remove(a[0]); p(f"  {C.GREEN}Destroyed.{C.RESET}")

    def cmd_whoami(self, a):
        s = self.state; print()
        p(f"  {C.STEEL}Alias:{C.RESET}     {C.BOLD}{C.CYAN}{s.player_name}{C.RESET}")
        p(f"  {C.STEEL}IP:{C.RESET}        {s.ip_address}")
        if s.vpn_active: p(f"  {C.STEEL}VPN IP:{C.RESET}    {random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}")
        p(f"  {C.STEEL}Level:{C.RESET}     {s.level}")
        cl = "LOW" if s.level < 3 else ("MED" if s.level < 5 else "HIGH")
        p(f"  {C.STEEL}Clearance:{C.RESET} {cl}"); print()

    def cmd_time(self, a): p(f"  {C.CYAN}{time.strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}")
    def cmd_history(self, a):
        print()
        for i, cmd in enumerate(self.history[-20:], max(1, len(self.history)-19)):
            p(f"  {C.DIM}{i:>4}{C.RESET}  {cmd}")
        print()
    def cmd_note(self, a):
        if not a: p("  [USAGE] note <text>", C.YELLOW); return
        self.state.notes.append(f"[{time.strftime('%H:%M')}] {' '.join(a)}"); p(f"  {C.GREEN}Saved.{C.RESET}")
    def cmd_notes(self, a):
        print()
        if not self.state.notes: p("  Empty. Use 'note <text>'.", C.DIM)
        for n in self.state.notes: p(f"    {C.CYAN}{n}{C.RESET}")
        print()
    def cmd_crypto(self, a):
        usd = self.state.crypto_wallet * 43000
        neon_box(f"BTC: {self.state.crypto_wallet:.6f} | ${usd:,.2f}", C.ORANGE)
    def cmd_netmap(self, a): clear(); netmap_anim()
    def cmd_whois(self, a):
        if not a or a[0] not in self.state.available_targets: p("  [ERROR] Unknown.", C.RED); return
        t = self.state.available_targets[a[0]]; print()
        glitch_text(f"  WHOIS - {a[0]}"); print()
        p(f"  {C.STEEL}Name:{C.RESET}     {t['name']}")
        p(f"  {C.STEEL}OS:{C.RESET}       {t['os']}")
        p(f"  {C.STEEL}Services:{C.RESET} {', '.join(t.get('services',[]))}")
        fw = f"{C.YELLOW}Yes (Lvl {t.get('firewall_level',0)}){C.RESET}" if t['firewall'] else f"{C.GREEN}No{C.RESET}"
        p(f"  {C.STEEL}Firewall:{C.RESET} {fw}")
        st = f"{C.GREEN}Compromised{C.RESET}" if t['compromised'] else f"{C.RED}Secured{C.RESET}"
        p(f"  {C.STEEL}Status:{C.RESET}   {st}"); print()
    def cmd_dns(self, a):
        if not a: p("  [USAGE] dns <domain>", C.YELLOW); return
        print(); p(f"  {C.BOLD}DNS: {a[0]}{C.RESET}")
        p(f"  {C.CYAN}A{C.RESET}    {random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}")
        p(f"  {C.CYAN}MX{C.RESET}   mail.{a[0]}"); p(f"  {C.CYAN}NS{C.RESET}   ns1.{a[0]}"); print()
    def cmd_spoof(self, a):
        mac = ':'.join(f'{random.randint(0,255):02x}' for _ in range(6))
        type_loading("Spoofing MAC", 1.5); p(f"  {C.GREEN}New MAC: {mac}{C.RESET}")
        self.state.detection_level = max(0, self.state.detection_level - 5)

    def cmd_phish(self, a):
        if "social_eng" not in self.state.tools: p("  [ERROR] social_eng needed.", C.RED); return
        if not a or a[0] not in self.state.available_targets: p("  [ERROR] Unknown target.", C.RED); return
        clear(); self.state.increase_detection(8); ip = a[0]
        print(); glitch_text(f"  PHISHING - {ip}"); print()
        type_loading("Cloning website", 1.5); type_loading("Sending emails", 2); type_loading("Waiting", 3)
        caught = random.randint(1, 10)
        if caught >= 3:
            t = self.state.available_targets[ip]
            p(f"\n  {C.GREEN}{caught} employees phished!{C.RESET}")
            self.state.known_passwords[ip] = t["password"]; self.state.add_xp(60); self.state.money += 300
        else:
            p(f"\n  {C.RED}Only {caught} clicked.{C.RESET}")
        print()

    def cmd_ddos(self, a):
        if "ddos_cannon" not in self.state.tools: p("  [ERROR] ddos_cannon needed.", C.RED); return
        if self.state.botnet_size < 10: p("  [ERROR] Need 10+ bots.", C.RED); return
        if not a: p("  [USAGE] ddos <ip>", C.YELLOW); return
        clear(); self.state.increase_detection(25)
        print(); glitch_text(f"  DDoS ATTACK - {a[0]}")
        p(f"  {C.BG_DARK_RED}{C.WHITE} LAUNCHING {self.state.botnet_size} BOTS {C.RESET}"); print()
        for _ in range(15):
            sys.stdout.write(f"\r  {C.RED}[ATTACK]{C.RESET} {self.state.botnet_size} bots | {C.YELLOW}{random.randint(100,9999)} Gbps{C.RESET}")
            sys.stdout.flush(); time.sleep(0.3)
        print("\n"); p(f"  {C.GREEN}Target DOWN!{C.RESET}"); self.state.add_xp(40); print()

    def cmd_wifihack(self, a):
        if "aircrack" not in self.state.tools: p("  [ERROR] aircrack needed.", C.RED); return
        clear(); print(); glitch_text("  WiFi CRACKER"); print()
        nets = [("HomeNet","WPA2"),("CoffeeShop","OPEN"),("NETGEAR-"+str(random.randint(1000,9999)),"WPA2"),("FBI_Van","WPA3")]
        for ssid, sec in nets:
            sc = C.GREEN if sec=="OPEN" else (C.YELLOW if sec=="WPA2" else C.RED)
            p(f"  {C.WHITE}{ssid:<25}{sc}{sec}{C.RESET} {random.randint(-30,-90)} dBm"); time.sleep(0.2)
        print(); target = input(f"  {C.CYAN}SSID to crack (cancel):{C.RESET} ").strip()
        if target == 'cancel': return
        type_loading("Capturing handshake", 3); hacker_bar("Cracking WPA2...", 4)
        if random.randint(1,100) <= 65:
            key = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
            neon_box(f"WiFi KEY: {key}", C.GREEN); self.state.add_xp(35); self.state.money += 100
        else:
            p(f"  {C.RED}[FAIL]{C.RESET}")
        print()

    def cmd_mine(self, a):
        if "crypto_miner" not in self.state.tools: p("  [ERROR] crypto_miner needed.", C.RED); return
        if not a: p("  [USAGE] mine <ip>", C.YELLOW); return
        if a[0] not in self.state.available_targets or not self.state.available_targets[a[0]]["compromised"]:
            p("  [ERROR] Not compromised.", C.RED); return
        print(); type_loading(f"Deploying miner on {a[0]}", 1.5)
        mined = 0.0
        for _ in range(15):
            amt = random.uniform(0.00001, 0.0005); mined += amt
            sys.stdout.write(f"\r  {C.ORANGE}[MINING]{C.RESET} {random.uniform(10,500):.1f} MH/s | {C.GOLD}{mined:.6f} BTC{C.RESET}")
            sys.stdout.flush(); time.sleep(0.4)
        self.state.crypto_wallet += mined
        print(f"\n\n  {C.GOLD}Mined {mined:.6f} BTC (${mined*43000:,.2f}){C.RESET}")
        self.state.add_xp(20); self.state.increase_detection(5); print()

    def cmd_analyze(self, a):
        if "forensics" not in self.state.tools: p("  [ERROR] forensics needed.", C.RED); return
        if not a or a[0] not in self.state.files: p("  [ERROR] File not found.", C.RED); return
        clear(); print(); glitch_text(f"  FORENSICS - {a[0]}"); print()
        type_loading("Analyzing", 1); type_loading("Extracting metadata", 1); type_loading("Hashing", 0.8)
        print(); h = hashlib.sha256(a[0].encode()).hexdigest()
        p(f"  {C.STEEL}SHA-256:{C.RESET} {C.DIM}{h}{C.RESET}")
        p(f"  {C.STEEL}Size:{C.RESET}    {random.randint(100,50000)} KB")
        p(f"  {C.STEEL}Author:{C.RESET}  {random.choice(['admin','root','system','unknown'])}")
        self.state.add_xp(15); print()

    def cmd_ransomware(self, a):
        if "ransomware" not in self.state.tools: p("  [ERROR] ransomware needed.", C.RED); return
        if not a: p("  [USAGE] ransomware <ip>", C.YELLOW); return
        ip = a[0]
        if ip not in self.state.available_targets or not self.state.available_targets[ip]["compromised"]:
            p("  [ERROR] Not compromised.", C.RED); return
        clear(); self.state.increase_detection(20)
        print(); glitch_text(f"  RANSOMWARE DEPLOY - {ip}"); print()
        type_loading("Encrypting target files", 3); type_loading("Dropping ransom note", 1)
        ransom = random.randint(1000, 10000)
        p(f"\n  {C.RED}{C.BOLD}ALL FILES ENCRYPTED!{C.RESET}")
        p(f"  {C.YELLOW}Ransom demand: ${ransom:,}{C.RESET}")
        if random.randint(1,100) <= 60:
            p(f"  {C.GREEN}Victim paid! +${ransom:,}{C.RESET}")
            self.state.money += ransom; self.state.add_xp(80)
        else:
            p(f"  {C.RED}Victim refused to pay.{C.RESET}"); self.state.add_xp(30)
        self.state.reputation += 10; print()

    def cmd_keylog(self, a):
        if "keylogger" not in self.state.tools: p("  [ERROR] keylogger needed.", C.RED); return
        if not a: p("  [USAGE] keylog <ip>", C.YELLOW); return
        ip = a[0]
        if ip not in self.state.available_targets or not self.state.available_targets[ip]["compromised"]:
            p("  [ERROR] Not compromised.", C.RED); return
        print(); type_loading(f"Installing keylogger on {ip}", 2)
        type_loading("Capturing keystrokes", 3); print()
        p(f"  {C.GREEN}Keystrokes captured:{C.RESET}")
        keystrokes = [
            f"admin typed: {self.state.available_targets[ip]['password']}",
            f"user typed: confidential meeting at 3pm",
            f"admin typed: transfer $50000 to account 4421",
            f"user typed: new server password is {random.choice(['Sup3rS3cur3!','L3tM31n','Ch@ng3M3'])}",
        ]
        for ks in random.sample(keystrokes, min(3, len(keystrokes))):
            p(f"    {C.YELLOW}>{C.RESET} {ks}"); time.sleep(0.5)
        self.state.add_xp(35); self.state.money += 200; print()

    def cmd_pivot(self, a):
        if not a: p("  [USAGE] pivot <ip>", C.YELLOW); return
        ip = a[0]
        if ip not in self.state.available_targets or not self.state.available_targets[ip]["compromised"]:
            p("  [ERROR] Not compromised.", C.RED); return
        print(); type_loading(f"Scanning internal network from {ip}", 2)
        internal = [f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(random.randint(3,8))]
        p(f"\n  {C.GREEN}Internal hosts discovered:{C.RESET}")
        for host in internal:
            services = random.sample(["SSH","HTTP","RDP","SMB","MySQL","FTP","SMTP"], random.randint(1,3))
            p(f"    {C.CYAN}{host:<18}{C.RESET} {', '.join(services)}")
            time.sleep(0.2)
        self.state.add_xp(25); print()

    def cmd_save(self, a):
        if self.net.online:
            self.sync_to_server()
            p(f"  {C.GREEN}Saved to server!{C.RESET}")
        else:
            p(f"  {C.YELLOW}Offline mode - progress in memory only.{C.RESET}")

    def cmd_leaderboard(self, a):
        clear()
        if self.net.online:
            resp = self.net.send({"action": "leaderboard", "sort_by": "reputation"})
            if resp.get("status") == "ok":
                lb = resp.get("leaderboard", [])
                print(); gprint("  === GLOBAL LEADERBOARD ===", (255,215,0), (255,100,0)); print()
                rc = [C.GOLD, C.SILVER, C.BRONZE]
                for i, e in enumerate(lb):
                    c = rc[i] if i < 3 else C.WHITE
                    on = f"{C.GREEN}ON{C.RESET}" if e.get("online") else f"{C.DIM}off{C.RESET}"
                    you = f" {C.PINK}<-YOU{C.RESET}" if e["name"] == self.net.username else ""
                    p(f"  {c}#{i+1}{C.RESET} {C.BOLD}{e['name']:<16}{C.RESET} Rep:{C.MAGENTA}{e.get('reputation',0):<8}{C.RESET} Lvl:{e.get('level',1):<4} {C.GOLD}${e.get('money',0):,}{C.RESET} [{on}]{you}")
                print(); return
        # Offline leaderboard
        print(); gprint("  === LEADERBOARD (OFFLINE) ===", (255,215,0), (255,100,0)); print()
        hackers = [("ZeroCool",random.randint(5000,99999),random.randint(5,10)),
                   ("AcidBurn",random.randint(5000,99999),random.randint(5,10)),
                   ("Phantom",random.randint(3000,50000),random.randint(4,9)),
                   (self.state.player_name, self.state.reputation, self.state.level),
                   ("N3tRunner",random.randint(500,20000),random.randint(2,7)),
                   ("DarkMatter",random.randint(100,10000),random.randint(1,6))]
        hackers.sort(key=lambda x: x[1], reverse=True)
        for i, (n, rep, lvl) in enumerate(hackers, 1):
            you = f" {C.PINK}<-YOU{C.RESET}" if n == self.state.player_name else ""
            p(f"  #{i} {C.BOLD}{n:<16}{C.RESET} Rep:{rep:<8} Lvl:{lvl}{you}")
        print()

    # ── ONLINE COMMANDS ──
    def cmd_online(self, a):
        if not self.net.online: p("  Not connected to server.", C.RED); return
        resp = self.net.send({"action": "online"})
        if resp.get("status") == "ok":
            players = resp.get("players", []); print()
            p(f"  {C.BOLD}Online ({resp.get('count',0)}):{C.RESET}")
            for pl in players: p(f"    {C.GREEN}*{C.RESET} {pl['name']} (Lvl {pl.get('level',1)})")
            if not players: p("    Just you!", C.DIM)
            print()

    def cmd_chat(self, a):
        if not self.net.online: p("  Not connected.", C.RED); return
        if not a: p("  [USAGE] chat <message>", C.YELLOW); return
        msg = " ".join(a)
        resp = self.net.send({"action":"chat","username":self.net.username,"message":msg})
        if resp.get("status") == "ok":
            p(f"  {C.STEEL}[{time.strftime('%H:%M:%S')}]{C.RESET} {C.CYAN}{self.net.username}{C.RESET}: {msg}")

    def cmd_chatlog(self, a):
        if not self.net.online: p("  Not connected.", C.RED); return
        resp = self.net.send({"action":"chat_history","count":20})
        if resp.get("status") == "ok":
            msgs = resp.get("messages", []); print()
            p(f"  {C.BOLD}Chat History:{C.RESET}")
            for m in msgs:
                p(f"  {C.STEEL}[{m.get('time','')}]{C.RESET} {C.CYAN}{m.get('user','?')}{C.RESET}: {m.get('text','')}")
            if not msgs: p("  No messages.", C.DIM)
            print()

    def cmd_profile(self, a):
        if not self.net.online: p("  Not connected.", C.RED); return
        if not a: p("  [USAGE] profile <name>", C.YELLOW); return
        resp = self.net.send({"action":"profile","target":a[0]})
        if resp.get("status") == "ok":
            pr = resp.get("profile", {}); print()
            on = f"{C.GREEN}ON{C.RESET}" if pr.get("online") else f"{C.RED}OFF{C.RESET}"
            p(f"  {C.BOLD}=== {pr.get('name','?')} ==={C.RESET} [{on}]")
            p(f"    Level: {pr.get('level',1)} | Money: {C.GOLD}${pr.get('money',0):,}{C.RESET} | Rep: {C.MAGENTA}{pr.get('reputation',0)}{C.RESET}")
            p(f"    Missions: {pr.get('missions',0)} | Last: {pr.get('last_login','?')}"); print()
        else: p(f"  {C.RED}Not found.{C.RESET}")

    def cmd_serverinfo(self, a):
        if not self.net.online: p("  Not connected.", C.RED); return
        resp = self.net.send({"action":"info"})
        if resp.get("status") == "ok":
            print(); p(f"  {C.BOLD}Server:{C.RESET} {resp.get('server','?')}")
            p(f"  Players: {resp.get('total_players',0)} | Online: {resp.get('online',0)}"); print()

    # ── OWNER PANEL ──
    def cmd_sudo(self, a):
        if not a or ' '.join(a) != "override-gamma-7": p("  [ERROR] Unknown command.", C.RED); return
        clear()
        while True:
            print(); gprint("  === OWNER PANEL ===", (255,0,100), (200,0,200)); print()
            for o in ["1.Money","2.Level","3.All tools","4.Compromise all","5.Reset detection",
                       "6.Complete missions","7.Add XP","8.Add crypto","9.GOD MODE","0.Exit"]:
                p(f"    {C.MAGENTA}{o}{C.RESET}")
            print(); ch = input(f"  {C.NEON_PINK}>>{C.RESET} ").strip()
            if ch=="1":
                try: self.state.money=int(input("  $: ")); p(f"  {C.GREEN}OK{C.RESET}")
                except: p("  Bad.",C.RED)
            elif ch=="2":
                try: self.state.level=int(input("  Lvl: ")); self.state.xp_to_next=int(100*(1.5**(self.state.level-1))); p(f"  {C.GREEN}OK{C.RESET}")
                except: p("  Bad.",C.RED)
            elif ch=="3":
                for t in self.state.shop_items:
                    if self.state.shop_items[t]["type"]=="tool" and t not in self.state.tools: self.state.tools.append(t)
                p(f"  {C.GREEN}All tools!{C.RESET}")
            elif ch=="4":
                for ip,t in self.state.available_targets.items(): t["compromised"]=True; self.state.known_passwords[ip]=t["password"]
                p(f"  {C.GREEN}All compromised!{C.RESET}")
            elif ch=="5": self.state.detection_level=0; self.state.heat_level=0; self.state.detected=False; p(f"  {C.GREEN}Reset.{C.RESET}")
            elif ch=="6":
                for m in self.missions.missions:
                    if not m["completed"]: m["completed"]=True; self.state.completed_missions.append(m["id"]); self.state.money+=m["reward_money"]; self.state.reputation+=m["reward_rep"]
                p(f"  {C.GREEN}All done!{C.RESET}")
            elif ch=="7":
                try: self.state.add_xp(int(input("  XP: ")))
                except: p("  Bad.",C.RED)
            elif ch=="8":
                try: self.state.crypto_wallet+=float(input("  BTC: ")); p(f"  {C.GREEN}OK{C.RESET}")
                except: p("  Bad.",C.RED)
            elif ch=="9":
                self.state.money=999999; self.state.level=10; self.state.reputation=99999
                self.state.detection_level=0; self.state.heat_level=0; self.state.vpn_active=True; self.state.proxy_chains=5
                self.state.botnet_size=100; self.state.crypto_wallet=100.0
                for t in self.state.shop_items:
                    if self.state.shop_items[t]["type"]=="tool" and t not in self.state.tools: self.state.tools.append(t)
                p(f"  {C.NEON_PINK}{C.BOLD}GOD MODE!{C.RESET}")
            elif ch=="0": clear(); self.show_banner(); return

    # ── MISSION CHECK ──
    def _check_missions(self, target_ip):
        for m in self.missions.missions:
            if m["target"] == target_ip and not m["completed"]:
                m["completed"] = True; self.state.completed_missions.append(m["id"])
                self.state.money += m["reward_money"]; self.state.reputation += m["reward_rep"]
                self.state.add_xp(m["reward_xp"])
                print(); gprint("  * ============================== *", (255,215,0), (255,100,0))
                fire_text(f"    MISSION: {m['title']}")
                p(f"  {C.GOLD}+${m['reward_money']:,}{C.RESET} {C.CYAN}+{m['reward_xp']}XP{C.RESET} {C.MAGENTA}+{m['reward_rep']}REP{C.RESET}")
                gprint("  * ============================== *", (255,100,0), (255,215,0))
                if all(mi["completed"] for mi in self.missions.missions):
                    self._victory()

    def _victory(self):
        clear(); matrix_rain(2); clear(); print()
        rainbow("  * * * * * * * * * * * * * * * * * * * *")
        gprint("       ALL MISSIONS COMPLETED!", (0,255,0), (0,255,255))
        gprint("        LEGENDARY HACKER", (255,215,0), (255,100,0))
        rainbow("  * * * * * * * * * * * * * * * * * * * *")
        print(); input(f"  {C.DIM}[ENTER for free mode]{C.RESET}")
        clear(); self.show_banner()

    def check_detection(self):
        if self.state.detected:
            clear(); matrix_rain(1); print()
            p(f"  {C.BG_RED}{C.WHITE}{C.BOLD}{'='*50}{C.RESET}")
            fire_text("             B U S T E D !")
            p(f"  {C.BG_RED}{C.WHITE}{C.BOLD}   YOUR IDENTITY HAS BEEN EXPOSED   {C.RESET}")
            p(f"  {C.BG_RED}{C.WHITE}{C.BOLD}{'='*50}{C.RESET}"); print()
            p(f"  Level: {self.state.level} | Money: ${self.state.money:,} | Missions: {len(self.state.completed_missions)}/{len(self.missions.missions)}")
            p(f"  Rep: {self.state.reputation} | Hacks: {self.state.hacks_successful}/{self.state.hacks_attempted}")
            if self.net.online: self.sync_to_server()
            print(); ch = input(f"  {C.YELLOW}Play again? (y/n):{C.RESET} ").strip().lower()
            if ch == 'y':
                self.state = GameState(); self.missions = MissionSystem(); self.run()
            else:
                if self.net.online: self.net.close()
                p(f"\n  {C.CYAN}Thanks for playing!{C.RESET}\n"); sys.exit(0)

    # ── COMMAND ROUTER ──
    def process(self, raw):
        parts = raw.strip().split()
        if not parts: return
        cmd = parts[0].lower(); args = parts[1:]
        self.history.append(raw)
        cmds = {
            "help":self.cmd_help,"status":self.cmd_status,"targets":self.cmd_targets,
            "missions":self.cmd_missions,"shop":self.cmd_shop,"buy":self.cmd_buy,
            "inventory":self.cmd_inventory,"tutorial":self.cmd_tutorial,
            "save":self.cmd_save,"whoami":self.cmd_whoami,"time":self.cmd_time,
            "history":self.cmd_history,"note":self.cmd_note,"notes":self.cmd_notes,
            "crypto":self.cmd_crypto,"leaderboard":self.cmd_leaderboard,
            "clear":lambda a:clear(),"cls":lambda a:clear(),
            "exit":lambda a:self.quit_game(),"quit":lambda a:self.quit_game(),
            "nmap":self.cmd_nmap,"ping":self.cmd_ping,"traceroute":self.cmd_traceroute,
            "connect":self.cmd_connect,"disconnect":self.cmd_disconnect,
            "netmap":self.cmd_netmap,"whois":self.cmd_whois,"dns":self.cmd_dns,
            "crack":self.cmd_crack,"firewall_bypass":self.cmd_firewall_bypass,
            "exploit":self.cmd_exploit,"sqlinject":self.cmd_sqlinject,
            "sniff":self.cmd_sniff,"bruteforce":self.cmd_bruteforce,
            "phish":self.cmd_phish,"ddos":self.cmd_ddos,"wifihack":self.cmd_wifihack,
            "ransomware":self.cmd_ransomware,"keylog":self.cmd_keylog,
            "download":self.cmd_download,"backdoor":self.cmd_backdoor,
            "clean_logs":self.cmd_clean_logs,"cat":self.cmd_cat,
            "mine":self.cmd_mine,"analyze":self.cmd_analyze,"pivot":self.cmd_pivot,
            "vpn":self.cmd_vpn,"proxy":self.cmd_proxy,
            "encrypt":self.cmd_encrypt,"shred":self.cmd_shred,"spoof":self.cmd_spoof,
            "sudo":self.cmd_sudo,
            "online":self.cmd_online,"chat":self.cmd_chat,"chatlog":self.cmd_chatlog,
            "profile":self.cmd_profile,"serverinfo":self.cmd_serverinfo,
            # NEW PVP & FACTION COMMANDS
            "players":self.cmd_players,"hack_player":self.cmd_hack_player,
            "track_player":self.cmd_track_player,"factions":self.cmd_factions,
            "join_faction":self.cmd_join_faction,"faction_quest":self.cmd_faction_quest,
            "create_faction":self.cmd_create_faction,
            "defenses":self.cmd_defenses,"attacks":self.cmd_attacks,"bounty":self.cmd_bounty,
            "war":self.cmd_war,"safehouse":self.cmd_safehouse,"events":self.cmd_events,
            "casino":self.cmd_casino,"dark_market":self.cmd_dark_market,
        }
        if cmd in cmds:
            cmds[cmd](args); self.auto_sync()
        else:
            p(f"  {C.RED}Unknown: '{cmd}'. Type 'help'.{C.RESET}")

    # ── PVP COMMANDS ──
    def cmd_players(self, a):
        if not self.net.online:
            p("  [ERROR] Need to be online.", C.RED)
            return
        clear()
        print()
        gprint("  === ONLINE HACKERS ===", (255,100,0), (255,50,50))
        print()
        resp = self.net.send({"action": "get_players"})
        if resp.get("status") == "ok":
            players = resp.get("players", [])
            for player in players:
                if player["name"] == self.net.username:
                    continue
                threat = "LOW" if player["level"] < self.state.level else ("MEDIUM" if player["level"] == self.state.level else "HIGH")
                tc = C.GREEN if threat == "LOW" else (C.YELLOW if threat == "MEDIUM" else C.RED)
                status = f"{C.GOLD}[ONLINE]{C.RESET}" if player.get("online") else f"{C.DIM}[OFFLINE]{C.RESET}"
                p(f"  {C.CYAN}{player['name']:<16}{C.RESET} Lvl:{player['level']:<3} Rep:{player['reputation']:<6} [{tc}{threat}{C.RESET}] {status}")
            print()
            p(f"  Type {C.GREEN}'hack_player <name>'{C.RESET} to attack")
        print()

    def cmd_hack_player(self, a):
        if not self.net.online:
            p("  [ERROR] Need to be online.", C.RED)
            return
        if not a:
            p("  [USAGE] hack_player <player_name>", C.YELLOW)
            return
        
        target_name = a[0]
        if target_name == self.net.username:
            p("  [ERROR] Can't hack yourself, genius.", C.RED)
            return
        
        self.state.hacks_attempted += 1
        self.state.increase_detection(20)
        self.state.heat_level = min(100, self.state.heat_level + 30)
        
        clear()
        print()
        glitch_text(f"  PLAYER EXPLOIT - {target_name}")
        print()
        
        resp = self.net.send({"action": "get_player_info", "target": target_name})
        if resp.get("status") != "ok":
            epic_fail("Target not found or offline!")
            return
        
        target = resp.get("player", {})
        target_level = target.get("level", 1)
        
        base_chance = 50
        if self.state.level > target_level:
            base_chance += (self.state.level - target_level) * 10
        else:
            base_chance -= (target_level - self.state.level) * 10
        
        if self.state.vpn_active:
            base_chance += 15
        
        if "firewall_upgrade" in target.get("tools", []):
            base_chance -= 20
        
        base_chance = max(10, min(90, base_chance))
        
        hacker_bar("Breaching defenses...", 3)
        
        if random.randint(1, 100) <= base_chance:
            self.state.hacks_successful += 1
            if target_name not in self.state.players_hacked:
                self.state.players_hacked.append(target_name)
            
            steal_amount = random.randint(100, min(500, target.get("money", 0) // 2))
            self.state.money += steal_amount
            
            print()
            p(f"  {C.BG_DARK_GREEN}{C.WHITE}{C.BOLD} HACK SUCCESSFUL! {C.RESET}")
            p(f"  {C.GREEN}Stole ${steal_amount:,} from {target_name}{C.RESET}")
            p(f"  {C.CYAN}+50 XP{C.RESET}")
            self.state.add_xp(50)
            self.state.reputation += 30
            
            self.net.send({
                "action": "notify",
                "target": target_name,
                "message": f"{self.net.username} hacked you and stole ${steal_amount:,}!"
            })
        else:
            print()
            p(f"  {C.BG_DARK_RED}{C.WHITE}{C.BOLD} HACK FAILED! {C.RESET}")
            p(f"  {C.RED}Their defenses were too strong.{C.RESET}")
            self.state.increase_detection(15)
            self.state.heat_level = min(100, self.state.heat_level + 20)
            
            if random.randint(1, 100) <= 30:
                p(f"  {C.YELLOW}WARNING: Target is tracing you!{C.RESET}")
                self.state.increase_detection(10)
        
        print()

    def cmd_track_player(self, a):
        if "player_tracker" not in self.state.tools:
            p("  [ERROR] player_tracker tool needed.", C.RED)
            return
        if not a:
            p("  [USAGE] track_player <name>", C.YELLOW)
            return
        
        if not self.net.online:
            p("  [ERROR] Need to be online.", C.RED)
            return
        
        print()
        type_loading(f"Tracking {a[0]}", 2)
        type_loading("Triangulating signal", 1.5)
        
        resp = self.net.send({"action": "get_player_info", "target": a[0]})
        if resp.get("status") == "ok":
            target = resp.get("player", {})
            print()
            p(f"  {C.GREEN}Target located:{C.RESET}")
            p(f"    Name: {target.get('name', '?')}")
            p(f"    Level: {target.get('level', '?')}")
            p(f"    Money: ${target.get('money', 0):,}")
            p(f"    Reputation: {target.get('reputation', 0)}")
            fake_ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            p(f"    Location: {fake_ip}")
            print()
        else:
            p(f"  {C.RED}Target not found.{C.RESET}")

    # ── FACTION COMMANDS ──
    def cmd_factions(self, a):
        clear()
        print()
        gprint("  === FACTIONS ===", (200,0,200), (100,0,200))
        print()
        for fid, f in self.state.faction_items.items():
            status = f"{C.GREEN}[JOINED Rank {self.state.faction_rank}]{C.RESET}" if self.state.faction == fid else ""
            p(f"  {f['color']}{f['name']:<20}{C.RESET} {C.DIM}{f['desc']}{C.RESET} {status}")
        print()
        p(f"  Type {C.GREEN}'join_faction <name>'{C.RESET} to join")
        print()

    def cmd_join_faction(self, a):
        if not a:
            p("  [USAGE] join_faction <red_team|blue_team|ghost_net|syndicate>", C.YELLOW)
            return
        fid = a[0].lower()
        if fid not in self.state.faction_items:
            p("  [ERROR] Unknown faction.", C.RED)
            return
        if self.state.faction:
            p(f"  [ERROR] Already in {self.state.faction_items[self.state.faction]['name']}.", C.RED)
            return
        self.state.faction = fid
        self.state.faction_rank = 1
        faction = self.state.faction_items[fid]
        clear()
        print()
        p(f"  {faction['color']}{C.BOLD}=== WELCOME TO {faction['name'].upper()} ==={C.RESET}")
        print()
        p(f"  {C.BOLD}You have joined {faction['color']}{faction['name']}{C.RESET}")
        p(f"  {C.DIM}{faction['desc']}{C.RESET}")
        p(f"  {C.YELLOW}Bonus: {faction['bonus']}{C.RESET}")
        print()
        self.state.add_xp(50)
        self.state.reputation += 20

    def cmd_faction_quest(self, a):
        if not self.state.faction:
            p("  [ERROR] Join a faction first.", C.RED)
            return
        faction = self.state.faction_items[self.state.faction]
        clear()
        print()
        p(f"  {faction['color']}{C.BOLD}=== {faction['name']} QUEST ==={C.RESET}")
        print()
        
        quests = {
            "red_team": [
                ("Sabotage Corporate Network", 5000, 200),
                ("DDoS rival faction", 3000, 150),
                ("Steal secret files", 4000, 180),
            ],
            "blue_team": [
                ("Defend against 5 attacks", 4000, 200),
                ("Patch critical vulnerabilities", 3500, 150),
                ("Find rogue hacker", 5000, 180),
            ],
            "ghost_net": [
                ("Complete 3 undetected hacks", 6000, 250),
                ("Gather intel on targets", 4000, 160),
                ("Stay hidden for 24hrs", 3000, 140),
            ],
            "syndicate": [
                ("Steal $50k from players", 5000, 220),
                ("Run extortion scheme", 4500, 190),
                ("Control 3 botnets", 6000, 200),
            ],
        }
        
        selected = random.choice(quests.get(self.state.faction, []))
        name, reward_xp, reward_rep = selected
        
        p(f"  {C.YELLOW}Quest: {name}{C.RESET}")
        p(f"  Difficulty: {C.ORANGE}{'*' * random.randint(2, 4)}{C.RESET}")
        p(f"  Reward: {C.CYAN}+{reward_xp} XP{C.RESET} {C.MAGENTA}+{reward_rep} Rep{C.RESET}")
        print()
        
        ch = input(f"  {C.GREEN}Accept? (y/n):{C.RESET} ").strip().lower()
        if ch == 'y':
            progress_bar("Completing quest", random.uniform(2, 4))
            self.state.add_xp(reward_xp)
            self.state.reputation += reward_rep
            self.state.faction_rank = min(5, self.state.faction_rank + 1)
            p(f"  {C.GREEN}Quest complete! Rank: {self.state.faction_rank}{C.RESET}")

    def cmd_defenses(self, a):
        clear()
        print()
        gprint("  === YOUR DEFENSES ===", (0,200,255), (0,100,200))
        print()
        p(f"  {C.BOLD}Security Systems:{C.RESET}")
        p(f"    Firewall: {C.GREEN if 'firewall_upgrade' in self.state.tools else C.RED}{'ON' if 'firewall_upgrade' in self.state.tools else 'OFF'}{C.RESET}")
        p(f"    Honeypot: {C.GREEN if 'honeypot' in self.state.tools else C.RED}{'ACTIVE' if 'honeypot' in self.state.tools else 'INACTIVE'}{C.RESET}")
        p(f"    VPN: {C.GREEN if self.state.vpn_active else C.RED}{'ON' if self.state.vpn_active else 'OFF'}{C.RESET}")
        p(f"    Proxies: {C.CYAN}{self.state.proxy_chains}{C.RESET}")
        print()
        p(f"  {C.BOLD}Recent Attacks:{C.RESET}")
        attacks = random.randint(0, 5)
        if attacks == 0:
            p(f"    {C.GREEN}None. You're safe.{C.RESET}")
        else:
            for _ in range(attacks):
                attacker = random.choice(["ZeroCool", "AcidBurn", "Phantom", "N3tRunner"])
                p(f"    {C.RED}[!]{C.RESET} {attacker} attempted breach")
        print()

    def cmd_attacks(self, a):
        clear()
        print()
        gprint("  === ATTACK LOG ===", (255,0,0), (200,0,0))
        print()
        if self.state.hacks_attempted == 0:
            p(f"  {C.DIM}No attacks yet.{C.RESET}")
        else:
            p(f"  Total Attempts: {self.state.hacks_attempted}")
            p(f"  Successful: {self.state.hacks_successful}")
            success_rate = (self.state.hacks_successful / self.state.hacks_attempted * 100) if self.state.hacks_attempted > 0 else 0
            p(f"  Success Rate: {C.YELLOW}{success_rate:.1f}%{C.RESET}")
            if self.state.players_hacked:
                print()
                p(f"  {C.BOLD}Hacked Players:{C.RESET}")
                for player in self.state.players_hacked:
                    p(f"    {C.RED}◆{C.RESET} {player}")
        print()

    def cmd_bounty(self, a):
        if not self.net.online:
            p("  [ERROR] Need to be online.", C.RED)
            return
        clear()
        print()
        gprint("  === BOUNTY BOARD ===", (255,100,0), (200,50,0))
        print()
        resp = self.net.send({"action": "get_bounties"})
        if resp.get("status") == "ok":
            bounties = resp.get("bounties", [])
            if not bounties:
                p(f"  {C.DIM}No bounties available.{C.RESET}")
            else:
                for bounty in bounties:
                    p(f"  {C.RED}{bounty['target']}{C.RESET}")
                    p(f"    Bounty: {C.GOLD}${bounty['reward']:,}{C.RESET}")
                    p(f"    Reason: {bounty['reason']}")
                    print()
        print()

    def cmd_war(self, a):
        if not self.state.faction:
            p("  [ERROR] Join a faction first.", C.RED)
            return
        clear()
        print()
        faction = self.state.faction_items[self.state.faction]
        gprint(f"  === {faction['name'].upper()} WAR STATUS ===", tuple([100]*3), tuple([200]*3))
        print()
        p(f"  {faction['color']}{faction['name']}{C.RESET}")
        p(f"    Members: {random.randint(5, 50)}")
        p(f"    Territory: {random.randint(1, 10)} servers")
        p(f"    Rival: {random.choice(['Red Team', 'Blue Team', 'Ghost Net', 'Syndicate'])}")
        print()
        print()

    def cmd_safehouse(self, a):
        clear()
        print()
        gprint("  === SAFEHOUSE ===", (100,100,255), (50,50,200))
        print()
        p(f"  {C.BOLD}Hideout Status:{C.RESET}")
        p(f"    Location: {random.choice(['Abandoned datacenter', 'Dark web node', 'Hidden server', 'Virtual machine'])}")
        p(f"    Security: {C.GREEN}HIGH{C.RESET}")
        p(f"    Detection Risk: {C.YELLOW if self.state.heat_level > 50 else C.GREEN}{self.state.heat_level}%{C.RESET}")
        print()
        p(f"  {C.BOLD}Options:{C.RESET}")
        p(f"    rest - Recover from heat (-20%)")
        p(f"    upgrade - Fortify defenses")
        print()

    def cmd_events(self, a):
        clear()
        print()
        gprint("  === WORLD EVENTS ===", (255,255,0), (200,200,0))
        print()
        events = [
            f"{C.RED}[ALERT]{C.RESET} FBI launches Operation Cyber Shield",
            f"{C.CYAN}[NEWS]{C.RESET} New zero-day discovered in Windows",
            f"{C.YELLOW}[THREAT]{C.RESET} Infamous hacker group active",
            f"{C.GREEN}[UPDATE]{C.RESET} New exploit framework released",
            f"{C.MAGENTA}[BOUNTY]{C.RESET} $100k reward for corporate secrets",
        ]
        for event in random.sample(events, min(3, len(events))):
            p(f"  {event}")
        print()

    def cmd_casino(self, a):
        clear()
        print()
        gprint("  === CRYPTO CASINO ===", (255,100,255), (200,50,200))
        print()
        p(f"  Balance: {C.GOLD}${self.state.money:,}{C.RESET}")
        print()
        p(f"  Games: roulette | blackjack | slots | dice")
        print()
        if a and a[0].lower() == "roulette":
            try:
                bet = int(a[1]) if len(a) > 1 else 100
                if bet > self.state.money:
                    p(f"  Insufficient funds.", C.RED)
                    return
                self.state.money -= bet
                if random.randint(1, 100) <= 45:
                    winnings = int(bet * random.uniform(1.5, 3))
                    self.state.money += winnings
                    p(f"  {C.GREEN}WON! +${winnings}{C.RESET}")
                else:
                    p(f"  {C.RED}Lost ${bet}{C.RESET}")
            except:
                p(f"  [USAGE] casino roulette <amount>", C.YELLOW)
        else:
            p(f"  Type: {C.GREEN}casino roulette <amount>{C.RESET}")
        print()

    def cmd_dark_market(self, a):
        clear()
        print()
        gprint("  === DARK WEB MARKET ===", (100,0,100), (50,0,50))
        fire_text("        * BLACK MARKET GOODS *")
        print()
        dark_items = {
            "exploit_kit": {"price": 5000, "desc": "Undetectable exploit"},
            "stolen_data": {"price": 2000, "desc": "Leaked databases"},
            "botnet_army": {"price": 15000, "desc": "1000 compromised hosts"},
            "fake_identity": {"price": 3000, "desc": "Spoof any nationality"},
            "quantum_key": {"price": 20000, "desc": "Unbreakable encryption"},
        }
        for item_id, item in dark_items.items():
            p(f"  {C.MAGENTA}{item_id:<20}{C.RESET} {C.GOLD}${item['price']:<8}{C.RESET} {C.DIM}{item['desc']}{C.RESET}")
        print()

    def quit_game(self):
        clear(); print()
        gprint("  =============================================", (100,100,100), (50,50,50))
        p(f"  {C.WHITE}Session terminated.{C.RESET}")
        if self.net.online:
            type_loading("Saving to server", 1)
            self.sync_to_server()
            self.net.send({"action":"logout","username":self.net.username,"game_state":self.state.to_dict()})
            self.net.close()
        type_loading("Wiping session", 0.8)
        p(f"\n  {C.CYAN}Goodbye, {self.state.player_name}.{C.RESET}")
        gprint("  =============================================", (50,50,50), (100,100,100))
        print(); sys.exit(0)

    def run(self):
        clear()
        print()
        gprint("    ╦ ╦╔═╗╔═╗╦╔═╔═╗╔╦╗╔═╗╦═╗╔╦╗", (0,255,100), (0,200,255))
        gprint("    ╠═╣╠═╣║  ╠╩╗╚═╗ ║ ║ ║╠╦╝║║║", (0,200,255), (100,100,255))
        gprint("    ╩ ╩╩ ╩╚═╝╩ ╩╚═╝ ╩ ╚═╝╩╚═╩ ╩", (100,100,255), (200,0,255))
        print()

        p(f"  {C.YELLOW}Connect to online server?{C.RESET}")
        p(f"  {C.DIM}(Enter server address or press ENTER for offline){C.RESET}")
        print()
        addr = input(f"  {C.CYAN}Server:{C.RESET} ").strip()

        if addr:
            host = addr; port = SERVER_PORT
            if ":" in host:
                parts = host.rsplit(":", 1); host = parts[0]
                try: port = int(parts[1])
                except: pass
            p(f"\n  Connecting to {host}:{port}...", C.YELLOW)
            if self.net.connect(host, port):
                p(f"  {C.GREEN}Connected!{C.RESET}")
                info = self.net.send({"action":"info"})
                if info.get("status") == "ok":
                    p(f"  {C.STEEL}{info.get('server','?')} | {info.get('total_players',0)} players | {info.get('online',0)} online{C.RESET}")
                print()
                while True:
                    p(f"  {C.GREEN}1{C.RESET} Login")
                    p(f"  {C.CYAN}2{C.RESET} Register")
                    p(f"  {C.RED}3{C.RESET} Play offline"); print()
                    ch = input(f"  {C.CYAN}>{C.RESET} ").strip()
                    if ch == "1":
                        print(); un = input(f"  {C.GREEN}Username:{C.RESET} ").strip()
                        pw = getpass.getpass(f"  {C.GREEN}Password:{C.RESET} ")
                        if un and pw:
                            p("  Logging in...", C.YELLOW)
                            resp = self.net.send({"action":"login","username":un,"password":pw})
                            if resp.get("status") == "ok":
                                self.net.username = un; self.state.player_name = un
                                gs = resp.get("game_state", {})
                                if gs: self.state.from_dict(gs)
                                self.missions.apply_save(self.state.completed_missions)
                                p(f"  {C.GREEN}{resp.get('message','Welcome!')}{C.RESET}")
                                time.sleep(1); break
                            else:
                                p(f"  {C.RED}{resp.get('message','Failed')}{C.RESET}"); print()
                    elif ch == "2":
                        print(); un = input(f"  {C.CYAN}Username:{C.RESET} ").strip()
                        pw = getpass.getpass(f"  {C.CYAN}Password:{C.RESET} ")
                        pw2 = getpass.getpass(f"  {C.CYAN}Confirm:{C.RESET} ")
                        if pw != pw2: p("  Passwords don't match.", C.RED); continue
                        if un and pw:
                            resp = self.net.send({"action":"register","username":un,"password":pw})
                            p(f"  {C.GREEN if resp.get('status')=='ok' else C.RED}{resp.get('message','')}{C.RESET}")
                        print()
                    elif ch == "3":
                        self.net.online = False; break
            else:
                p(f"  {C.RED}Can't connect. Playing offline.{C.RESET}")
                self.net.online = False
                time.sleep(1)
        else:
            name = input(f"\n  {C.GREEN}Hacker alias:{C.RESET} ").strip()
            if name: self.state.player_name = name

        self.boot()
        getpass.getpass(f"  {C.GREEN}Password:{C.RESET} ")
        type_loading("Authenticating", 1); type_loading("Loading profile", 0.6)
        print(); decrypt_anim(f"Welcome back, {self.state.player_name}.")
        time.sleep(1); clear(); self.show_banner()

        if not self.state.tutorial_done:
            ch = input(f"  {C.CYAN}Tutorial? (y/n):{C.RESET} ").strip().lower()
            if ch == 'y': self.cmd_tutorial([])
            else: self.state.tutorial_done = True; p(f"  Type {C.GREEN}'tutorial'{C.RESET} anytime.\n")

        while self.running:
            try:
                self.check_detection()
                user_input = input(self.get_prompt())
                self.process(user_input)
            except KeyboardInterrupt:
                print(f"\n  {C.YELLOW}Use 'exit' to quit.{C.RESET}")
            except EOFError:
                self.quit_game()

if __name__ == "__main__":
    game = HackStorm()
    game.run()
