from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import cycle
import time
import os
from tqdm import tqdm
from termcolor import colored
from threading import Lock
from globals import (
    global_live_hosts, global_tested_proxies, stop_event, pause_event
)
from modules.scanner_utils import send_tcp_probe  # Ensure `send_tcp_probe` is in a utility module


# Global lock for thread-safe operations
lock = Lock()

# Lock for thread-safe operations
lock = Lock()

# Counters for progress tracking
counter_scanned = 0
counter_valid = 0
counter_failed = 0
counter_total = 0
counter_remaining = 0

# Function to update the counters display dynamically
def display_counters():
    print("\033[H\033[J", end="")  # Clear terminal screen
    print(f"[STATS] "
          f"{colored(f'Scanned: {counter_scanned}', 'blue')} | "
          f"{colored(f'Valid: {counter_valid}', 'green')} | "
          f"{colored(f'Failed: {counter_failed}', 'red')} | "
          f"{colored(f'Remaining: {counter_remaining}', 'yellow')} | "
          f"{colored(f'Total: {counter_total}', 'white')}"
    )

def scan_single_host(host, proxy):
    """
    Scan a single host using the given proxy and return its banner if available.

    :param host: Target host IP address.
    :param proxy: SOCKS5 proxy (IP, Port).
    :return: Tuple (host, banner) if successful, None otherwise.
    """
    global counter_scanned, counter_valid, counter_failed, counter_remaining

    try:
        # Check for stop or pause
        while pause_event.is_set():
            time.sleep(0.5)

        if stop_event.is_set():
            return None

        banner = send_tcp_probe(host, proxy)
        with lock:
            counter_scanned += 1
            counter_remaining -= 1
            if banner:
                counter_valid += 1
                print(colored(f"[VALID] {host}: {banner}", "green"))
                return f"{host}: {banner}"
            else:
                counter_failed += 1
                print(colored(f"[FAILED] {host} - No banner received", "red"))

        display_counters()
        
    except Exception as e:
        with lock:
            counter_failed += 1
            counter_remaining -= 1
        print(colored(f"[ERROR] {host} - {e}", "red"))
        display_counters()

    return None

def scan_hosts():
    """
    Scan hosts in global_live_hosts using proxies from global_tested_proxies.
    Perform a banner check on port 22 using multithreading.
    """
    global counter_scanned, counter_valid, counter_failed, counter_total, counter_remaining

    if not global_live_hosts:
        print("[ERROR] No live hosts available for scanning.")
        return

    if not global_tested_proxies:
        print("[ERROR] No tested proxies available for scanning.")
        return

    print("[INFO] Starting multithreaded host scan...")

    proxy_cycle = cycle(global_tested_proxies)  # Cycle through proxies
    results = []

    # Initialize counters
    counter_scanned = 0
    counter_valid = 0
    counter_failed = 0
    counter_total = len(global_live_hosts)
    counter_remaining = len(global_live_hosts)

    display_counters()  # Initial counter display

    # Use ThreadPoolExecutor with max_workers = 12 for concurrency
    with ThreadPoolExecutor(max_workers=12) as executor:
        future_to_host = {
            executor.submit(scan_single_host, host, next(proxy_cycle)): host
            for host in global_live_hosts
        }

        # Monitor progress with tqdm
        for future in tqdm(as_completed(future_to_host), total=len(future_to_host), desc="Scanning Hosts"):
            # Check for stop event
            if stop_event.is_set():
                print("[INFO] Stopping scanning...")
                break

            # Wait if paused
            while pause_event.is_set():
                time.sleep(0.5)

            result = future.result()
            if result:
                results.append(result)

    # Save scan results
    results_file = "results/scanned_hosts.txt"
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    with open(results_file, "w") as file:
        file.writelines(f"{line}\n" for line in results)

    print(f"[INFO] Scan complete. Results saved to {results_file}.")
def show_results():
    """
    Display the scan results.
    """
    results_file = "results/scanned_hosts.txt"
    if not os.path.exists(results_file):
        print("[ERROR] No results found. Perform a scan first.")
        return

    with open(results_file, "r") as file:
        results = file.read()
        print("[INFO] Scan Results:\n")
        print(results)

def clear_results():
    """
    Clear the scan results file.
    """
    results_file = "results/scanned_hosts.txt"
    if os.path.exists(results_file):
        os.remove(results_file)
        print("[INFO] Results file cleared.")
    else:
        print("[INFO] No results file to clear.")
