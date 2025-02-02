import os
import time
import subprocess
import threading
from globals import global_config
import socket
import sys

# Default Tor Control Port
TOR_CONTROL_PORT = 9051

def start_tor():
    """
    Start the Tor service if not already running.
    """
    print("[INFO] Starting Tor service...")
    try:
        # Try to start Tor using systemd (Linux-based systems)
        subprocess.run(["sudo", "systemctl", "start", "tor"], check=True)
        print("[INFO] Tor service started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to start Tor: {e}")
        sys.exit(1)  # Exit the application if Tor can't be started

def stop_tor():
    """
    Stop the Tor service.
    """
    print("[INFO] Stopping Tor service...")
    try:
        subprocess.run(["sudo", "systemctl", "stop", "tor"], check=True)
        print("[INFO] Tor service stopped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to stop Tor: {e}")
        sys.exit(1)

def renew_tor_ip():
    """
    Send a signal to Tor to get a new identity (renew IP).
    """
    print("[INFO] Renewing Tor IP address...")

    try:
        # Using netcat to send the signal to Tor's control port
        subprocess.run(
            ["echo", "signal NEWNYM", "|", "nc", "localhost", str(TOR_CONTROL_PORT)],
            check=True
        )
        print("[INFO] Tor IP address renewed successfully.")
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to renew Tor IP. Ensure Tor control port is enabled (9051).")

def check_tor_connection():
    """
    Check if Tor is running and listening on the expected control port.
    """
    try:
        with socket.create_connection(("localhost", TOR_CONTROL_PORT), timeout=5):
            print("[INFO] Tor is running and listening on the control port.")
            return True
    except socket.error:
        print("[ERROR] Tor is not running or control port is not accessible.")
        return False

def renew_loop():
    """
    Continuously renew Tor IP every interval specified in config.
    """
    while True:
        if global_config["tor_usage"] and check_tor_connection():
            renew_tor_ip()
        time.sleep(global_config["tor_renew_interval"])

# Start the Tor renewal loop in a background thread if Tor usage is enabled
if global_config.get("tor_usage", False):
    threading.Thread(target=renew_loop, daemon=True).start()
