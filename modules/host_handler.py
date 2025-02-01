from globals import global_hosts, global_live_hosts, pause_event, stop_event
import os
import ipaddress
import csv
import random
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from termcolor import colored

# Global lock for thread-safe operations
lock = Lock()

# Ensure the results directory exists
os.makedirs("results", exist_ok=True)

# Counters for progress tracking
counter_valid = 0
counter_dead = 0
counter_total = 0
counter_remaining = 0

def display_counters():
    """
    Display real-time counters in the terminal.
    """
    print("\033[H\033[J", end="")  # Clear terminal screen
    print(f"[STATS] "
          f"{colored(f'Valid: {counter_valid}', 'green')} | "
          f"{colored(f'Dead: {counter_dead}', 'red')} | "
          f"{colored(f'Remaining: {counter_remaining}', 'yellow')} | "
          f"{colored(f'Total: {counter_total}', 'white')}")

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

def load_previous_hosts():
    """
    Load previously tested live hosts from the results file.

    :return: List of previously tested hosts.
    """
    live_hosts_file = "results/live_hosts.txt"
    if not os.path.exists(live_hosts_file):
        print(colored("[ERROR] No previously tested hosts found.", "red"))
        return []

    with open(live_hosts_file, "r") as file:
        tested_hosts = [line.strip() for line in file if line.strip()]

    print(colored(f"[INFO] Loaded {len(tested_hosts)} previously tested live hosts.", "green"))
    return tested_hosts

def load_ip_ranges():
    """
    Load IP ranges from CSV files within country-named folders in the ip_ranges directory.
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

    # Prepare output directory for calculated IPs
    ip_addresses_dir = os.path.join(country_dir, "ip_addresses")
    if not os.path.exists(ip_addresses_dir):
        os.makedirs(ip_addresses_dir)

    output_file = os.path.join(ip_addresses_dir, f"{selected_country}IPV4List.txt")

    # Process the selected file
    all_ips = []
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        for line in reader:
            if len(line) != 2:
                print(f"[ERROR] Invalid IP range format: {line}")
                continue
            try:
                start_ip = ipaddress.IPv4Address(line[0].strip())
                end_ip = ipaddress.IPv4Address(line[1].strip())

                if start_ip > end_ip:
                    print(f"[ERROR] Start IP {start_ip} is greater than End IP {end_ip}.")
                    continue

                current_ip = start_ip
                while current_ip <= end_ip:
                    all_ips.append(str(current_ip))
                    current_ip += 1

            except ValueError:
                print(f"[ERROR] Invalid IP range: {line}")

    random.shuffle(all_ips)  # Shuffle the IP list for randomness
    global_hosts = all_ips

    # Save the calculated IPs to a file
    with open(output_file, "w") as output:
        for ip in global_hosts:
            output.write(ip + "\n")

    print(f"[INFO] Loaded {len(global_hosts)} IPs from {file_path} and saved to {output_file}.")
    return global_hosts

def test_single_host(host, min_delay=1, max_delay=3):
    """
    Test connectivity to a single host with optional delays.
    
    :param host: Host to test.
    :param min_delay: Minimum delay between scans.
    :param max_delay: Maximum delay between scans.
    """
    global counter_valid, counter_dead, counter_remaining

    try:
        # Pause execution if requested
        while pause_event.is_set():
            time.sleep(0.5)

        # Stop execution if requested
        if stop_event.is_set():
            print("[INFO] Scanning stopped.")
            return

        # Simulate a scan (replace with actual scanning logic)
        time.sleep(random.uniform(min_delay, max_delay))

        # If successful, mark host as live
        with lock:
            global_live_hosts.append(host)
            with open("results/live_hosts.txt", "a") as file:
                file.write(f"{host}\n")

            counter_valid += 1
            counter_remaining -= 1
            display_counters()
            print(colored(f"[VALID] {host}", "green"))

    except Exception as e:
        with lock:
            counter_dead += 1
            counter_remaining -= 1
            display_counters()
        print(colored(f"[DEAD] {host}: {e}", "red"))

def test_hosts(hosts):
    """
    Test connectivity to multiple hosts using multi-threading.

    :param hosts: List of hosts to test.
    :return: List of live hosts.
    """
    global global_live_hosts, counter_valid, counter_dead, counter_remaining, counter_total
    global_live_hosts = []  # Clear previous live hosts

    if not hosts:
        print("[ERROR] No hosts to test.")
        return []

    counter_valid = 0
    counter_dead = 0
    counter_total = len(hosts)
    counter_remaining = len(hosts)

    display_counters()

    print("[INFO] Testing host connectivity with a thread limit of 12...")

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(test_single_host, host): host for host in hosts}

        for future in tqdm(as_completed(futures), total=len(futures), desc="Testing Hosts"):
            if stop_event.is_set():
                print("[INFO] Stopping scanning...")
                break

            while pause_event.is_set():
                time.sleep(0.5)

            try:
                future.result()
            except Exception as e:
                host = futures[future]
                print(colored(f"[ERROR] Error testing host {host}: {e}", "yellow"))

            display_counters()

    print(f"[INFO] Found {len(global_live_hosts)} live hosts.")
    return global_live_hosts
