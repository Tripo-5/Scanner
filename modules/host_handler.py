from globals import global_hosts, global_live_hosts
import os
import ipaddress
from tqdm import tqdm
import random

def load_hosts():
    """
    Load hosts from a file into the global_hosts variable.
    """
    global global_hosts
    file_path = input("Enter the path to the hosts file: ")
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return []

    with open(file_path, "r") as file:
        global_hosts = [line.strip() for line in file if line.strip()]
    print(f"[INFO] Loaded {len(global_hosts)} hosts from {file_path}.")
    return global_hosts

def load_ip_ranges():
    """
    Load IP ranges from CSV files within country-named folders in the ip_ranges directory,
    expand them into individual IPs, and store them in global_hosts.
    """
    global global_hosts

    base_dir = "ip_ranges"
    if not os.path.exists(base_dir):
        print(f"[ERROR] Base directory {base_dir} does not exist.")
        return []

    # List available countries
    countries = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not countries:
        print(f"[INFO] No country directories found in {base_dir}.")
        return []

    print("[INFO] Available countries:")
    for i, country in enumerate(countries, start=1):
        print(f"{i}. {country}")

    try:
        country_choice = int(input("Select a country by number: ")) - 1
        if country_choice < 0 or country_choice >= len(countries):
            print("[ERROR] Invalid selection.")
            return []
    except ValueError:
        print("[ERROR] Invalid input. Please enter a number.")
        return []

    selected_country = countries[country_choice]
    country_dir = os.path.join(base_dir, selected_country)

    # List available CSV files in the selected country folder
    csv_files = [f for f in os.listdir(country_dir) if f.endswith(".csv")]
    if not csv_files:
        print(f"[INFO] No CSV files found in {country_dir}.")
        return []

    print(f"[INFO] Available IP range files in {selected_country}:")
    for i, csv_file in enumerate(csv_files, start=1):
        print(f"{i}. {csv_file}")

    try:
        file_choice = int(input("Select a file by number: ")) - 1
        if file_choice < 0 or file_choice >= len(csv_files):
            print("[ERROR] Invalid selection.")
            return []
    except ValueError:
        print("[ERROR] Invalid input. Please enter a number.")
        return []

    selected_file = csv_files[file_choice]
    file_path = os.path.join(country_dir, selected_file)

    # Process the selected file
    all_ips = []
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            try:
                network = ipaddress.ip_network(line, strict=False)
                all_ips.extend(str(ip) for ip in network.hosts())
            except ValueError:
                print(f"[ERROR] Invalid IP range: {line}")

    random.shuffle(all_ips)  # Shuffle the IP list for randomness
    global_hosts = all_ips
    print(f"[INFO] Loaded {len(global_hosts)} IPs from {file_path}.")
    return global_hosts

def test_hosts(hosts, proxies):
    """
    Test connectivity to hosts and update global_live_hosts.

    :param hosts: List of hosts to test.
    :param proxies: List of proxies to use for testing.
    :return: List of live hosts.
    """
    global global_live_hosts
    global_live_hosts = []  # Clear previous live hosts

    if not hosts:
        print("[ERROR] No hosts to test.")
        return []

    print("[INFO] Testing host connectivity...")
    for host in tqdm(hosts, desc="Testing Hosts"):
        try:
            # Replace with actual connectivity logic (e.g., ping or TCP connection test)
            is_live = True  # Simulated result
            if is_live:
                global_live_hosts.append(host)
        except Exception as e:
            print(f"[ERROR] Failed to test host {host}: {e}")

    print(f"[INFO] Found {len(global_live_hosts)} live hosts.")
    return global_live_hosts
