import threading

# Global Events
pause_event = threading.Event()
stop_event = threading.Event()

# Global Data Storage
global_scraped_proxies = []  # Stores proxies before testing
global_tested_proxies = []  # Stores successfully tested proxies
global_hosts = []  # Stores loaded hosts
global_live_hosts = []  # Stores live hosts after testing
global_vulnerable_hosts = []  # Stores vulnerable hosts

# Configuration for scanning, proxies, and other modules
global_config = {
    "proxy_usage": False,
    "scan_timeout": 5,  # Default timeout for scans
    "max_threads": 10,  # Maximum threads for parallel execution
}

# Task Tracking
active_tasks = {}

# Proxy, Host, and Bruteforce Statistics
proxy_stats = {"total": 0, "testing": 0, "valid": 0, "dead": 0, "remaining": 0}
host_stats = {"total": 0, "scanning": 0, "valid": 0, "dead": 0, "remaining": 0}
brute_stats = {"running": 0, "success": 0, "failed": 0}

# Web Server Config
web_config = {
    "enabled": False,
    "host": "0.0.0.0",
    "port": 5000
}
