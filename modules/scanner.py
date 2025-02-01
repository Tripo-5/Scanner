from globals import global_live_hosts, global_tested_proxies, pause_event, stop_event
from itertools import cycle
import socks
import socket
import os
import time
import threading
from tqdm import tqdm
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor, as_completed

# Global lock for thread-safe operations
lock = threading.Lock()

# Ensure the results directory exists
os.makedirs("results", exist_ok=True)

# Counters for progress tracking
counter_scanned = 0
counter_failed = 0
counter_total = 0
counter_remaining = 0

# Function to update the counters display
def display_counters():
    print("\033[H\033[J", end="")  # Clear terminal screen
    print(f"[STATS] "
          f"{colored(f'Scanned: {counter_scanned}', 'green')} | "
          f"{colored(f'Failed: {counter_failed}', 'red')} | "
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
    Scan a single host using a SOCKS5 proxy.
    
    :param host: The target host.
    :param proxy: The proxy being used for the scan.
    """
    global counter_scanned, counter_failed, counter_remaining

    # Check for pause or stop
    while pause_event.is_set():
        time.sleep(0.5)

    if stop_event.is_set():
        print("[INFO] Scanning stopped.")
        return

    try:
        banner = send_tcp_probe(host, proxy)
        if banner:
            with lock:
                with open("results/scanned_hosts.txt", "a") as file:
                    file.write(f"{host}: {banner}\n")

                counter_scanned += 1
                counter_remaining -= 1

                display_counters()
                print(colored(f"[INFO] {host}: {banner}", "green"))
        else:
            raise ValueError("No banner received")

    except Exception as e:
        with lock:
            counter_failed += 1
            counter_remaining -= 1
            display_counters()
        print(colored(f"[ERROR] Error scanning host {host}: {e}", "red"))

def scan_hosts():
    """
    Scan hosts in global_live_hosts using proxies from global_tested_proxies.
    Perform a banner check on port 22.
    """
    global counter_scanned, counter_failed, counter_total, counter_remaining

    if not global_live_hosts:
        print("[ERROR] No live hosts available for scanning.")
        return

    if not global_tested_proxies:
        print("[ERROR] No tested proxies available for scanning.")
        return

    proxy_cycle = cycle(global_tested_proxies)  # Cycle through proxies

    # Initialize counters
    counter_scanned = 0
    counter_failed = 0
    counter_total = len(global_live_hosts)
    counter_remaining = len(global_live_hosts)

    # Clear previous scan results
    with open("results/scanned_hosts.txt", "w") as file:
        pass

    display_counters()

    print("[INFO] Starting host scan...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(scan_single_host, host, next(proxy_cycle)): host for host in global_live_hosts}

        for future in tqdm(as_completed(futures), total=len(futures), desc="Scanning Hosts"):
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
                print(colored(f"[ERROR] Error scanning host {host}: {e}", "red"))

            display_counters()

    print(f"[INFO] Scan complete. Results saved to results/scanned_hosts.txt.")

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
