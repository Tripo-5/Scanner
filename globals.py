import threading

# Global lists to store data across different modules
global_hosts = []
global_live_hosts = []
global_vulnerable_hosts = []
global_scraped_proxies = []
global_tested_proxies = []
global_active_sessions = []
global_generated_payloads = []
global_error_log = []
global_scan_stats = []
global_wordlist_paths = []

# Global configuration dictionary
global_config = {
    "tor_usage": False,
    "tor_renew_interval": 60,
    "proxy_usage": False,
    "max_scan_threads": 10,
    "scan_timeout": 5,
    "auto_save_results": True,
}

# Pause and Stop events for controlling execution flow
pause_event = threading.Event()
stop_event = threading.Event()
