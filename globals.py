import threading

# Global Events
pause_event = threading.Event()
stop_event = threading.Event()

# Task Tracking
active_tasks = {}

# Proxy & Host Scanning Stats
proxy_stats = {"total": 0, "testing": 0, "valid": 0, "dead": 0, "remaining": 0}
host_stats = {"total": 0, "scanning": 0, "valid": 0, "dead": 0, "remaining": 0}
brute_stats = {"running": 0, "success": 0, "failed": 0}

# Web Server Config
web_config = {
    "enabled": False,
    "host": "0.0.0.0",
    "port": 5000
}
