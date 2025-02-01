import os
import time
import subprocess
import threading
from globals import global_config

TOR_CONTROL_PORT = 9051  # Default Tor control port

def start_tor():
    """
    Start the Tor service if not already running.
    """
    print("[INFO] Starting Tor service...")
    try:
        subprocess.run(["systemctl", "start", "tor"], check=True)
        print("[INFO] Tor service started successfully.")
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to start Tor. Ensure Tor is installed.")

def stop_tor():
    """
    Stop the Tor service.
    """
    print("[INFO] Stopping Tor service...")
    try:
        subprocess.run(["systemctl", "stop", "tor"], check=True)
        print("[INFO] Tor service stopped.")
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to stop Tor.")

def renew_tor_ip():
    """
    Send a signal to Tor to get a new identity (renew IP).
    """
    print("[INFO] Renewing Tor IP address...")
    try:
        subprocess.run(
            ["echo", "signal NEWNYM", "|", "nc", "localhost", str(TOR_CONTROL_PORT)],
            check=True
        )
        print("[INFO] Tor IP address renewed successfully.")
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to renew Tor IP. Ensure Tor control port is enabled.")

def renew_loop():
    """
    Continuously renew Tor IP every interval specified in config.
    """
    while True:
        if global_config["tor_usage"]:
            renew_tor_ip()
        time.sleep(global_config["tor_renew_interval"])

# Start renewal loop in background if Tor is enabled
if global_config["tor_usage"]:
    threading.Thread(target=renew_loop, daemon=True).start()
