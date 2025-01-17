# Global Variables

# Session Tracking
global_active_sessions = []  # Tracks active C2 sessions

# Hosts Management
global_hosts = []  # Stores all loaded hosts
global_live_hosts = []  # Stores live hosts detected during testing
global_vulnerable_hosts = []  # Stores hosts identified as vulnerable

# Proxy Management
global_scraped_proxies = []  # Stores proxies before testing
global_tested_proxies = []  # Stores proxies after testing

# Configuration Settings
global_config = {}  # Stores dynamic configuration settings loaded from config.json

# Generated Payloads
global_generated_payloads = []  # Tracks paths to recently generated reverse shells or cryptominers

# Error Logs
global_error_log = []  # Stores error messages for debugging purposes

# Scan Statistics
global_scan_stats = {
    "scanned": 0,        # Number of hosts scanned
    "live": 0,           # Number of live hosts detected
    "vulnerable": 0      # Number of vulnerable hosts detected
}

# Wordlist Paths
global_wordlist_paths = {
    "usernames": "wordlists/ssh_usernames.txt",
    "passwords": "wordlists/ssh_passwords.txt",
}
