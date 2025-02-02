from globals import global_hosts, global_live_hosts, pause_event, stop_event
import os
import ipaddress
import csv
import random
import time
import socks
import socket
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from termcolor import colored
from itertools import cycle
from threading import Lock

# Ensure results directory exists
os.makedirs("results", exist_ok=True)

# Global lock for thread-safe operations
lock = Lock()

# Counters for tracking progress
counter_valid = 0
counter_dead = 0
counter_total = 0
counter_remaining = 0

# Function to display live counters
def display_counters():
    print("\033[H\033[J", end="")  # Clear terminal screen
    print(f"[STATS] "
          f"{colored(f'Valid: {counter_valid}', 'green')} | "
          f"{colored(f'Dead: {counter_dead}', 'red')} | "
          f"{colored(f'Remaining: {counter_remaining}', 'yellow')} | "
          f"{colored(f'Total: {counter_total}', 'white')}")

# Load hosts from file
def load_hosts():
    """
    Load hosts from a file into the global_hosts list.
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

# Load IP ranges from CSV files
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

    # List country folders
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

    # List CSV files in selected country folder
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

    # Prepare output directory for calculated IPs
    ip_addresses_dir = os.path.join(country_dir, "ip_addresses")
    os.makedirs(ip_addresses_dir, exist_ok=True)

    output_file = os.path.join(ip_addresses_dir, f"{selected_country}_IPV4List.txt")

    # Process the selected file
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

    # Save IPs to file
    with open(output_file, "w") as output:
        for ip in global_hosts:
            output.write(ip + "\n")

    print(f"[INFO] Loaded {len(global_hosts)} IPs from {file_path} and saved to {output_file}.")
    return global_hosts

# Load previously tested hosts
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

# Test individual host connectivity using SOCKS5 proxy
# Fix: Correctly apply proxies & validate format
def test_single_host(host, proxy=None, min_delay=1, max_delay=3):
    """
    Test a single host's connectivity via a SOCKS5 proxy with random delay.

    :param host: Target host to test
    :param proxy: SOCKS5 proxy to use (IP:PORT)
    :param min_delay: Minimum delay between scans (seconds)
    :param max_delay: Maximum delay between scans (seconds)
    """
    global counter_valid, counter_dead, counter_remaining

    try:
        sock = socks.socksocket()
        
        # Validate and set proxy
        if proxy:
            if isinstance(proxy, list):  
                proxy = ":".join(proxy)  # Convert ["IP", "PORT"] to "IP:PORT"
            
            proxy_host, proxy_port = proxy.split(":")
            proxy_port = int(proxy_port)

            if not (0 <= proxy_port <= 65535):
                print(colored(f"[ERROR] Invalid proxy port: {proxy_port}", "red"))
                return

            sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)

        while pause_event.is_set():
            time.sleep(0.5)

        if stop_event.is_set():
            print("[INFO] Scanning stopped.")
            return

        sock.settimeout(5)
        sock.connect((host, 22))  # Try connecting to SSH port
        sock.close()

        with lock:
            global_live_hosts.append(host)
            with open("results/live_hosts.txt", "a") as file:
                file.write(f"{host}\n")

            counter_valid += 1
            counter_remaining -= 1
            display_counters()
            print(colored(f"[VALID] {host} (via {proxy})", "green"))

    except (socket.timeout, socks.ProxyError, socks.GeneralProxyError) as e:
        with lock:
            counter_dead += 1
            counter_remaining -= 1
            display_counters()
        print(colored(f"[DEAD] {host} (via {proxy}) - {e}", "red"))

    except Exception as e:
        print(colored(f"[ERROR] Unexpected error testing {host}: {e}", "red"))

    finally:
        # Introduce random delay between scans
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
# Multithreaded host testing
def test_hosts(hosts, proxies):
    """
    Test multiple hosts for connectivity using multithreading and SOCKS proxies.

    :param hosts: List of hosts to test
    :param proxies: List of SOCKS5 proxies
    :return: List of live hosts
    """
    global global_live_hosts, counter_valid, counter_dead, counter_remaining, counter_total
    global_live_hosts = []

    if not hosts:
        print("[ERROR] No hosts to test.")
        return []

    if not proxies:
        print("[ERROR] No proxies available for testing.")
        return []

    counter_valid = 0
    counter_dead = 0
    counter_total = len(hosts)
    counter_remaining = len(hosts)

    # Clear previous live hosts file
    with open("results/live_hosts.txt", "w"):
        pass

    display_counters()

    proxy_cycle = cycle(proxies)  # Cycle through proxies correctly

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(test_single_host, host, next(proxy_cycle)): host for host in hosts}

        for future in tqdm(as_completed(futures), total=len(futures), desc="Testing Hosts"):
            if stop_event.is_set():
                print("[INFO] Stopping scanning...")
                break

            while pause_event.is_set():
                time.sleep(0.5)

            display_counters()

    print(f"[INFO] Found {len(global_live_hosts)} live hosts.")
    return global_live_hosts
