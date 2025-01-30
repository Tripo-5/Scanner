from globals import global_hosts, global_live_hosts, pause_event, stop_event
import os
import ipaddress
from tqdm import tqdm
import random
import csv
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from termcolor import colored
import time
import socks
import socket
from itertools import cycle


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
    calculate all IPs within the ranges, and save them to global_hosts.
    Additionally, save the calculated IPs to a file.
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


# Global lock for thread-safe operations
lock = Lock()

# Ensure the results directory exists
os.makedirs("results", exist_ok=True)

# Counters for progress tracking
counter_valid = 0
counter_dead = 0
counter_total = 0
counter_remaining = 0

# Function to update the counters display
def display_counters():
    print("\033[H\033[J", end="")  # Clear terminal screen
    print(f"[STATS] "
          f"{colored(f'Valid: {counter_valid}', 'green')} | "
          f"{colored(f'Dead: {counter_dead}', 'red')} | "
          f"{colored(f'Remaining: {counter_remaining}', 'yellow')} | "
          f"{colored(f'Total: {counter_total}', 'white')}")

def test_single_host(host, proxy=None, min_delay=1, max_delay=3):
    """
    Test connectivity to a single host via a SOCKS proxy with random delay.

    :param host: Host to test.
    :param proxy: SOCKS proxy to use for the connection (IP:Port format).
    :param min_delay: Minimum delay between scans (in seconds).
    :param max_delay: Maximum delay between scans (in seconds).
    """
    global counter_valid, counter_dead, counter_remaining
    try:
        # Parse the proxy if provided
        if proxy:
            proxy_host, proxy_port = proxy.split(":")
            proxy_port = int(proxy_port)

        # Set up a SOCKS socket
        sock = socks.socksocket()
        if proxy:
            sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)

        # Check for pause or stop
        while pause_event.is_set():
            time.sleep(0.5)

        if stop_event.is_set():
            print("[INFO] Scanning stopped.")
            return

        # Attempt to connect to the host on port 22
        sock.settimeout(5)  # Set a timeout for the connection
        sock.connect((host, 22))
        sock.close()

        # If the connection is successful, record the host as live
        with lock:
            global_live_hosts.append(host)
            with open("results/live_hosts.txt", "a") as file:
                file.write(f"{host}\n")

            # Update counters
            counter_valid += 1
            counter_remaining -= 1

            # Update display
            display_counters()
            print(colored(f"[VALID] {host} (via SOCKS proxy {proxy})", "green"))

    except Exception as e:
        # Handle dead hosts
        with lock:
            counter_dead += 1
            counter_remaining -= 1
            display_counters()
        print(colored(f"[DEAD] {host} (via SOCKS proxy {proxy}): {e}", "red"))

    # Introduce random delay between scans
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def test_hosts(hosts, proxies):
    """
    Test connectivity to multiple hosts using SOCKS proxies, multithreading, and random delays.

    :param hosts: List of hosts to test.
    :param proxies: List of SOCKS proxies to use for testing (each as a [IP, Port] list).
    :return: List of live hosts.
    """
    global global_live_hosts, counter_valid, counter_dead, counter_remaining, counter_total
    global_live_hosts = []  # Clear previous live hosts

    if not hosts:
        print("[ERROR] No hosts to test.")
        return []

    if not proxies:
        print("[ERROR] No proxies available for testing.")
        return []

    # Initialize counters
    counter_valid = 0
    counter_dead = 0
    counter_total = len(hosts)
    counter_remaining = len(hosts)

    # Clear previous live hosts file
    with open("results/live_hosts.txt", "w") as file:
        pass  # Clear contents by opening in write mode

    display_counters()

    print("[INFO] Testing host connectivity using SOCKS proxies with a thread limit of 12...")

    # Use ThreadPoolExecutor with a maximum of 12 threads
    with ThreadPoolExecutor(max_workers=12) as executor:
        # Cycle through proxies for each host
        proxy_cycle = cycle(proxies)

        # Submit all host tests as tasks
        futures = {
            executor.submit(
                test_single_host, host, f"{proxy[0]}:{proxy[1]}"
            ): host for host, proxy in zip(hosts, proxy_cycle)
        }

        # Use tqdm to display progress
        for future in tqdm(as_completed(futures), total=len(futures), desc="Testing Hosts"):
            # Check for stop event
            if stop_event.is_set():
                print("[INFO] Stopping scanning...")
                break

            # Wait if paused
            while pause_event.is_set():
                time.sleep(0.5)

            try:
                future.result()  # Ensure exceptions are raised
            except Exception as e:
                host = futures[future]
                print(colored(f"[ERROR] Error testing host {host}: {e}", "yellow"))

            # Update dynamic stats after each test
            display_counters()

    print(f"[INFO] Found {len(global_live_hosts)} live hosts.")
    return global_live_hosts

def load_tested_hosts():
    """
    Load previously tested live hosts from results/live_hosts.txt.
    """
    global global_live_hosts
    if not os.path.exists("results/live_hosts.txt"):
        print("[ERROR] No previously tested hosts found.")
        return []
    with open("results/live_hosts.txt", "r") as file:
        global_live_hosts = [line.strip() for line in file if line.strip()]
    print(f"[INFO] Loaded {len(global_live_hosts)} previously tested hosts.")
    return global_live_hosts
