from globals import global_hosts, global_live_hosts, pause_event, stop_event
import os
import ipaddress
import csv
import random
import time
import socks
import socket
import threading
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from termcolor import colored
from itertools import cycle
from collections import deque

# Ensure results directory exists
os.makedirs("results", exist_ok=True)

# Global lock for thread-safe operations
lock = threading.Lock()

# Host scanning statistics
host_stats = {"total": 0, "scanning": 0, "valid": 0, "dead": 0, "remaining": 0}

# Limit for displaying recently tested hosts
PRINT_LIMIT = 20

# Store the most recent hosts tested
recent_hosts = deque(maxlen=PRINT_LIMIT)

def load_previous_hosts():
    """
    Load previously tested live hosts from results/live_hosts.txt.
    """
    global global_hosts
    live_hosts_file = "results/live_hosts.txt"

    if not os.path.exists(live_hosts_file):
        print("[ERROR] No previously tested live hosts found.")
        return []

    with open(live_hosts_file, "r") as file:
        global_hosts = [line.strip() for line in file if line.strip()]

    print(f"[INFO] Loaded {len(global_hosts)} previously tested live hosts.")
    return global_hosts

def load_ip_ranges():
    """
    Load IP ranges from CSV files within the ip_ranges directory.
    Convert ranges into individual IPs and save them for processing.
    """
    global global_hosts
    base_dir = "ip_ranges"

    if not os.path.exists(base_dir):
        print(f"[ERROR] Base directory {base_dir} does not exist.")
        return []

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

    ip_addresses_dir = os.path.join(country_dir, "ip_addresses")
    os.makedirs(ip_addresses_dir, exist_ok=True)

    output_file = os.path.join(ip_addresses_dir, f"{selected_country}_IPV4List.txt")

    all_ips = []
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        for line in reader:
            if len(line) != 2:
                continue
            try:
                start_ip = ipaddress.IPv4Address(line[0].strip())
                end_ip = ipaddress.IPv4Address(line[1].strip())

                if start_ip > end_ip:
                    continue

                current_ip = start_ip
                while current_ip <= end_ip:
                    all_ips.append(str(current_ip))
                    current_ip += 1

            except ValueError:
                continue

    random.shuffle(all_ips)
    global_hosts = all_ips

    with open(output_file, "w") as output:
        for ip in global_hosts:
            output.write(ip + "\n")

    print(f"[INFO] Loaded {len(global_hosts)} IPs from {file_path} and saved to {output_file}.")
    return global_hosts


def load_hosts():
    """Load hosts from a file into the global_hosts list."""
    global global_hosts
    file_path = input("Enter the path to the hosts file: ")
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return []

    with open(file_path, "r") as file:
        global_hosts = [line.strip() for line in file if line.strip()]
    print(f"[INFO] Loaded {len(global_hosts)} hosts from {file_path}.")
    return global_hosts


def test_hosts(hosts, proxies):
    """Test multiple hosts for connectivity using multithreading."""
    if not hosts:
        print("[ERROR] No hosts to test. Load hosts first.")
        return []

    if not proxies:
        print("[ERROR] No proxies available. Load tested proxies first.")
        return []

    global host_stats
    host_stats.update({"total": len(hosts), "scanning": len(hosts), "valid": 0, "dead": 0, "remaining": len(hosts)})

    print("[INFO] Host scanning started...")

    def background_scanning():
        with ThreadPoolExecutor(max_workers=12) as executor:
            proxy_cycle = cycle(proxies)
            futures = {executor.submit(test_single_host, host, next(proxy_cycle)): host for host in hosts}

            for future in tqdm(as_completed(futures), total=len(futures), desc="Testing Hosts"):
                host = futures[future]
                result = future.result()

                if result:
                    host_stats["valid"] += 1
                    recent_hosts.append([host, "Valid"])
                else:
                    host_stats["dead"] += 1
                    recent_hosts.append([host, "Dead"])

                host_stats["remaining"] -= 1

                # Update status dynamically
                print_status()

    # Start host scanning in the background
    scanning_thread = threading.Thread(target=background_scanning, daemon=True)
    scanning_thread.start()


def print_status():
    """Update the terminal display dynamically with counters."""
    print("\r{} | {} | {} | {}".format(
        colored(f"Valid Hosts: {host_stats['valid']}", "green"),
        colored(f"Dead Hosts: {host_stats['dead']}", "red"),
        colored(f"Remaining: {host_stats['remaining']}", "yellow"),
        colored(f"Total: {host_stats['total']}", "white")
    ), end="")

    print("\nMost recent hosts tested:")
    for host_info in reversed(recent_hosts):
        host_str, status = host_info
        color = "green" if status == "Valid" else "red"
        print(colored(f"{host_str} - {status}", color))


def test_single_host(host, proxy=None):
    """Test a single host's connectivity via a SOCKS5 proxy."""
    while pause_event.is_set():
        time.sleep(0.5)

    if stop_event.is_set():
        print("[INFO] Stopping host tests.")
        return False

    try:
        # Ensure proxy format is correct
        if isinstance(proxy, list):
            proxy = ":".join(proxy)

        proxy_host, proxy_port = proxy.split(":")
        proxy_port = int(proxy_port)

        if not (0 <= proxy_port <= 65535):
            print(colored(f"[ERROR] Invalid proxy port: {proxy_port}", "red"))
            return False

        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
        sock.settimeout(5)
        sock.connect((host, 22))  # Test SSH port connection
        sock.close()

        with lock:
            global_live_hosts.append(host)
            with open("results/live_hosts.txt", "a") as file:
                file.write(f"{host}\n")

        return True

    except (socket.timeout, socks.ProxyError, socks.GeneralProxyError):
        return False


def save_live_hosts():
    """Save the successfully tested live hosts to file."""
    with open("results/live_hosts.txt", "w") as file:
        for host in global_live_hosts:
            file.write(f"{host}\n")
    print(f"[INFO] Live hosts saved to results/live_hosts.txt.")


def load_live_hosts():
    """Load previously tested live hosts from results/live_hosts.txt."""
    global global_live_hosts

    if not os.path.exists("results/live_hosts.txt"):
        print("[ERROR] No previously tested live hosts found.")
        return []

    with open("results/live_hosts.txt", "r") as file:
        global_live_hosts = [line.strip() for line in file if line.strip()]

    print(f"[INFO] Loaded {len(global_live_hosts)} previously tested live hosts.")
    return global_live_hosts


def clear_live_hosts():
    """Clear the list of previously tested live hosts."""
    open("results/live_hosts.txt", "w").close()
    global_live_hosts.clear()
    print("[INFO] Cleared all previously tested live hosts.")
