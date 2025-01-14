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
    Load IP ranges from a file, expand them into individual IPs, and store them in global_hosts.
    """
    global global_hosts
    file_path = input("Enter the path to the IP ranges file: ")
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return []

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
