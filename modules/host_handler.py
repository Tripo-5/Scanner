from globals import global_hosts, global_live_hosts, pause_event, stop_event
import os
import ipaddress
from tqdm import tqdm
import random
import csv
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from termcolor import colored
import time
import socks
import socket
from itertools import cycle

# Global lock for thread-safe operations
lock = threading.Lock()

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
        sock.settimeout(5)
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
    :param proxies: List of SOCKS proxies to use for testing.
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
                future.result()
            except Exception as e:
                host = futures[future]
                print(colored(f"[ERROR] Error testing host {host}: {e}", "yellow"))

            # Update dynamic stats after each test
            display_counters()

    print(f"[INFO] Found {len(global_live_hosts)} live hosts.")
    return global_live_hosts
