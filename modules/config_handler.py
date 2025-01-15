import json
import os
import socket

CONFIG_FILE = "config.json"

# Default configuration settings
default_config = {
    "save_progress": True,
    "enable_reverse_shell": False,
    "listening_port": 4444,
    "listening_ip": "0.0.0.0",
    "enable_ddns": False,       # Option to enable DDNS
    "ddns_domain": "",          # DDNS domain name
}


def load_config():
    """
    Load or create the configuration file.

    :return: Dictionary containing the configuration settings.
    """
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as file:
            json.dump(default_config, file, indent=4)
        print(f"[INFO] Created default configuration file: {CONFIG_FILE}")

    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    return config


def save_config(config):
    """
    Save the given configuration to the configuration file.

    :param config: Dictionary containing configuration settings.
    """
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)
    print(f"[INFO] Configuration saved to {CONFIG_FILE}.")


def resolve_ddns(domain):
    """
    Resolve the IP address for a DDNS domain.

    :param domain: The DDNS domain name.
    :return: The resolved IP address, or None if resolution fails.
    """
    try:
        ip_address = socket.gethostbyname(domain)
        print(f"[INFO] Resolved DDNS domain '{domain}' to IP: {ip_address}")
        return ip_address
    except socket.gaierror:
        print(f"[ERROR] Failed to resolve DDNS domain: {domain}")
        return None


def configure_settings():
    """
    Display and modify configuration settings.
    """
    config = load_config()

    print("\n[ Configuration Settings ]")
    print(f"1.) Save Progress: {config['save_progress']}")
    print(f"2.) Enable Reverse Shell: {config['enable_reverse_shell']}")
    print(f"3.) Listening IP: {config['listening_ip']}")
    print(f"4.) Listening Port: {config['listening_port']}")
    print(f"5.) Enable DDNS: {config['enable_ddns']}")
    print(f"6.) DDNS Domain: {config['ddns_domain']}")
    print("7.) Exit Settings")

    while True:
        choice = input("Select a setting to modify (or 7 to exit): ").strip()

        if choice == "1":
            config["save_progress"] = not config["save_progress"]
            print(f"[INFO] Save Progress set to {config['save_progress']}.")
        elif choice == "2":
            config["enable_reverse_shell"] = not config["enable_reverse_shell"]
            print(f"[INFO] Enable Reverse Shell set to {config['enable_reverse_shell']}.")
        elif choice == "3":
            new_ip = input("Enter new Listening IP: ").strip()
            config["listening_ip"] = new_ip
            print(f"[INFO] Listening IP set to {config['listening_ip']}.")
        elif choice == "4":
            try:
                new_port = int(input("Enter new Listening Port: ").strip())
                config["listening_port"] = new_port
                print(f"[INFO] Listening Port set to {config['listening_port']}.")
            except ValueError:
                print("[ERROR] Invalid port. Please enter a valid integer.")
        elif choice == "5":
            config["enable_ddns"] = not config["enable_ddns"]
            print(f"[INFO] Enable DDNS set to {config['enable_ddns']}.")
        elif choice == "6":
            new_domain = input("Enter DDNS Domain: ").strip()
            config["ddns_domain"] = new_domain
            print(f"[INFO] DDNS Domain set to {config['ddns_domain']}.")
        elif choice == "7":
            break
        else:
            print("[ERROR] Invalid choice. Please select a valid option.")

    save_config(config)


def setup_reverse_shell_listener():
    """
    Setup the reverse shell listener based on configuration.
    """
    config = load_config()

    if config["enable_reverse_shell"]:
        ip = config["listening_ip"]
        if config["enable_ddns"] and config["ddns_domain"]:
            resolved_ip = resolve_ddns(config["ddns_domain"])
            ip = resolved_ip if resolved_ip else ip

        port = config["listening_port"]
        print(f"[INFO] Setting up reverse shell listener on {ip}:{port}")

        # Logic for starting the listener (e.g., using socket)
