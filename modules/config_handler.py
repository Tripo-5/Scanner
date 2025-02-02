import json
import os
import time
import threading
from globals import global_config, stop_event, pause_event  # Fixed missing imports

CONFIG_FILE = "config.json"

def load_config():
    """
    Load configuration settings from config.json, ensuring default values exist.
    """
    default_config = {
        "tor_usage": False,
        "tor_renew_interval": 60,
        "proxy_usage": False,
        "max_scan_threads": 10,
        "scan_timeout": 5,
        "auto_save_results": True,
        "db_config": {
            "host": "localhost",
            "user": "root",
            "password": "password",
            "database": "scanner_db"
        }
    }

    if not os.path.exists(CONFIG_FILE):
        print("[INFO] Configuration file not found. Creating default settings.")
        save_config(default_config)  # Create a new config file
        return default_config

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

        # Ensure all required keys exist
        for key, value in default_config.items():
            if key not in config:
                print(f"[WARNING] Missing config key: {key}. Adding default value.")
                config[key] = value  # Add missing keys with default values

        save_config(config)  # Save updated config
        return config

    except (json.JSONDecodeError, IOError) as e:
        print(f"[ERROR] Failed to load config: {e}")
        return default_config  # Return default settings if file is corrupted


def save_config(config):
    """
    Save configuration settings to config.json.
    """
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        print("[INFO] Configuration settings saved.")
    except IOError as e:
        print(f"[ERROR] Failed to save config: {e}")

# Load config globally
global_config = load_config()  # Fixed issue with update

def configure_settings():
    """
    Interactive menu to configure the settings.
    """
    while True:
        print("\n[ Configuration Settings ]")
        print("1.) Toggle Tor Usage (Current: {})".format("Enabled" if global_config["tor_usage"] else "Disabled"))
        print("2.) Toggle Proxy Usage (Current: {})".format("Enabled" if global_config["proxy_usage"] else "Disabled"))
        print("3.) Set Max Scan Threads (Current: {})".format(global_config["max_scan_threads"]))
        print("4.) Set Scan Timeout (Current: {}s)".format(global_config["scan_timeout"]))
        print("5.) Set Tor Renew Interval (Current: {}s)".format(global_config["tor_renew_interval"]))
        print("6.) Enable/Disable Auto-Save Results (Current: {})".format(
            "Enabled" if global_config["auto_save_results"] else "Disabled"))
        print("7.) Save & Exit")
        print("8.) Exit Without Saving")

        choice = input("Enter your choice: ")

        if choice == "1":
            global_config["tor_usage"] = not global_config["tor_usage"]
            print("[INFO] Tor usage set to:", global_config["tor_usage"])
        elif choice == "2":
            global_config["proxy_usage"] = not global_config["proxy_usage"]
            print("[INFO] Proxy usage set to:", global_config["proxy_usage"])
        elif choice == "3":
            try:
                max_threads = int(input("Enter max scan threads (default: 10): "))
                if max_threads > 0:
                    global_config["max_scan_threads"] = max_threads
            except ValueError:
                print("[ERROR] Invalid input. Must be a number.")
        elif choice == "4":
            try:
                scan_timeout = int(input("Enter scan timeout in seconds (default: 5): "))
                if scan_timeout > 0:
                    global_config["scan_timeout"] = scan_timeout
            except ValueError:
                print("[ERROR] Invalid input. Must be a number.")
        elif choice == "5":
            try:
                renew_interval = int(input("Enter Tor renew interval in seconds (default: 60): "))
                if renew_interval > 0:
                    global_config["tor_renew_interval"] = renew_interval
            except ValueError:
                print("[ERROR] Invalid input. Must be a number.")
        elif choice == "6":
            global_config["auto_save_results"] = not global_config["auto_save_results"]
            print("[INFO] Auto-save results set to:", global_config["auto_save_results"])
        elif choice == "7":
            save_config(global_config)  # Fixed missing argument
            print("[INFO] Configuration saved. Returning to main menu.")
            break
        elif choice == "8":
            print("[INFO] Discarding changes. Returning to main menu.")
            break
        else:
            print("[ERROR] Invalid choice. Please select a valid option.")

def renew_tor_connection():
    """
    Force a new Tor circuit connection.
    This will pause scanning, renew the connection, and then resume scanning.
    """
    print("[INFO] Renewing Tor connection...")

    # Pause scanning while renewing the Tor connection
    pause_event.set()

    try:
        # Using subprocess instead of os.system for better control
        print("[INFO] Sending signal to Tor to get a new identity...")
        subprocess.run(["sudo", "systemctl", "reload", "tor"], check=True)
        
        # Give Tor some time to reconnect
        time.sleep(3)
        print("[INFO] Tor connection renewed successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to renew Tor connection: {e}")

    except Exception as e:
        print(f"[ERROR] Unexpected error during Tor renewal: {e}")
    
    # Resume scanning
    pause_event.clear()


def auto_renew_tor():
    """
    Automatically renew Tor connections at set intervals.
    This runs in a background thread.
    """
    def renew_loop():
        while not stop_event.is_set():
            if global_config["tor_usage"]:
                renew_tor_connection()
            time.sleep(global_config["tor_renew_interval"])

    threading.Thread(target=renew_loop, daemon=True).start()

# Load configuration at startup
load_config()
auto_renew_tor()
