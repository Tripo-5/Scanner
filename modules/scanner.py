from globals import (
    global_live_hosts, global_tested_proxies,
    pause_event, stop_event
)
import socks
import socket
import os
import time
import random
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from termcolor import colored
from itertools import cycle

# Ensure results directory exists
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

def send_tcp_probe(ip, proxy, port=22):
    """
    Perform a banner grab on the given IP and port using a SOCKS5 proxy.

    :param ip: Target IP address
    :param proxy: Proxy details (host and port)
    :param port: Target port (default: 22)
    :return: Banner string if successful, None otherwise
    """
    proxy_host, proxy_port = proxy
    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, proxy_host, int(proxy_port))
        sock.settimeout(5)  # Set a 5-second timeout
        sock.connect((ip, port))
        sock.sendall(b"\n")  # Send a newline to initiate the banner response
        banner = sock.recv(1024).decode("utf-8", errors="ignore")
        sock.close()
        return banner.strip()
    except (socket.error, socks.ProxyError, socks.GeneralProxyError):
        return None

def scan_single_host(host, proxy):
    """
    Scan a single host for SSH banners.

    :param host: Target host IP
    :param proxy: SOCKS5 Proxy (IP:Port format)
    """
    global counter_valid, counter_dead, counter_remaining
    try:
        # Pause & Stop handling
        while pause_event.is_set():
            time.sleep(0.5)
        if stop_event.is_set():
            print("[INFO] Scanning stopped.")
            return None

        # Perform banner grab
        banner = send_tcp_probe(host, proxy)

        if banner:
            with open("results/scanned_hosts.txt", "a") as file:
                file.write(f"{host}: {banner}\n")

            # Update counters
            counter_valid += 1
            counter_remaining -= 1
            display_counters()
            print(colored(f"[VALID] {host}: {banner}", "green"))
            return host, banner
        else:
            raise Exception("No banner retrieved.")

    except Exception as e:
        counter_dead += 1
        counter_remaining -= 1
        display_counters()
        print(colored(f"[DEAD] {host}: {e}", "red"))
        return None

def scan_hosts():
    """
    Scan hosts in global_live_hosts using proxies from global_tested_proxies.
    Perform a banner check on port 22.
    """
    global counter_valid, counter_dead, counter_remaining, counter_total
    if not global_live_hosts:
        print("[ERROR] No live hosts available for scanning.")
        return

    if not global_tested_proxies:
        print("[ERROR] No tested proxies available for scanning.")
        return

    # Initialize counters
    counter_valid = 0
    counter_dead = 0
    counter_total = len(global_live_hosts)
    counter_remaining = len(global_live_hosts)

    # Clear previous scan results
    open("results/scanned_hosts.txt", "w").close()

    display_counters()
    print("[INFO] Starting multi-threaded host scan...")

    # Cycle through proxies
    proxy_cycle = cycle(global_tested_proxies)

    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {
            executor.submit(scan_single_host, host, next(proxy_cycle)): host
            for host in global_live_hosts
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Scanning Hosts"):
            if stop_event.is_set():
                print("[INFO] Stopping scanning...")
                break

            while pause_event.is_set():
                tqdm.write("[INFO] Scanning paused. Press F5 to resume.")
                time.sleep(0.5)

            try:
                future.result()
            except Exception as e:
                host = futures[future]
                print(colored(f"[ERROR] Error scanning host {host}: {e}", "yellow"))

            display_counters()

    print(f"[INFO] Scan complete. Found {counter_valid} live hosts.")
    print("[INFO] Results saved to results/scanned_hosts.txt.")

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
