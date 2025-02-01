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
