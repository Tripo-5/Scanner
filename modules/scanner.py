from globals import global_live_hosts, global_tested_proxies, pause_event, stop_event
import socks
import socket
import os
import time
import threading
from tqdm import tqdm
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import cycle
from collections import deque

# Ensure the results directory exists
os.makedirs("results", exist_ok=True)

# Global lock for thread-safe operations
lock = threading.Lock()

# Scanning statistics
scan_stats = {"total": 0, "scanning": 0, "scanned": 0, "failed": 0, "remaining": 0}

# Limit for displaying recently scanned hosts
PRINT_LIMIT = 20

# Store the most recent scanned hosts
recent_scans = deque(maxlen=PRINT_LIMIT)


def send_tcp_probe(ip, proxy, port=22):
    """Perform a banner grab on the given IP using a SOCKS5 proxy."""
    proxy_host, proxy_port = proxy
    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, proxy_host, int(proxy_port))
        sock.settimeout(5)
        sock.connect((ip, port))
        sock.sendall(b"\n")
        banner = sock.recv(1024).decode("utf-8", errors="ignore")
        sock.close()
        return banner.strip()
    except (socket.error, socks.ProxyError, socks.GeneralProxyError):
        return None


def scan_single_host(host, proxy):
    """Scan a single host using a SOCKS5 proxy."""
    global scan_stats

    while pause_event.is_set():
        time.sleep(0.5)

    if stop_event.is_set():
        print("[INFO] Scanning stopped.")
        return False

    try:
        banner = send_tcp_probe(host, proxy)
        if banner:
            with lock:
                with open("results/scanned_hosts.txt", "a") as file:
                    file.write(f"{host}: {banner}\n")

                scan_stats["scanned"] += 1
                scan_stats["remaining"] -= 1
                recent_scans.append([host, "Success"])

                print_status()
                print(colored(f"[INFO] {host}: {banner}", "green"))
            return True
        else:
            raise ValueError("No banner received")

    except Exception as e:
        with lock:
            scan_stats["failed"] += 1
            scan_stats["remaining"] -= 1
            recent_scans.append([host, "Failed"])
            print_status()
        print(colored(f"[ERROR] Error scanning host {host}: {e}", "red"))
        return False


def scan_hosts():
    """Scan hosts in global_live_hosts using proxies from global_tested_proxies."""
    if not global_live_hosts:
        print("[ERROR] No live hosts available for scanning.")
        return

    if not global_tested_proxies:
        print("[ERROR] No tested proxies available for scanning.")
        return

    global scan_stats
    scan_stats.update({"total": len(global_live_hosts), "scanning": len(global_live_hosts), "scanned": 0, "failed": 0, "remaining": len(global_live_hosts)})

    print("[INFO] Host scanning started...")

    def background_scanning():
        with ThreadPoolExecutor(max_workers=10) as executor:
            proxy_cycle = cycle(global_tested_proxies)
            futures = {executor.submit(scan_single_host, host, next(proxy_cycle)): host for host in global_live_hosts}

            for future in tqdm(as_completed(futures), total=len(futures), desc="Scanning Hosts"):
                host = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(colored(f"[ERROR] Error scanning host {host}: {e}", "red"))
                print_status()

    # Start scanning in the background
    scanning_thread = threading.Thread(target=background_scanning, daemon=True)
    scanning_thread.start()


def print_status():
    """Update the terminal display dynamically with counters."""
    print("\r"
          + colored(f"Successful Scans: {scan_stats['scanned']}", "green") + " | "
          + colored(f"Failed: {scan_stats['failed']}", "red") + " | "
          + colored(f"Remaining: {scan_stats['remaining']}", "yellow") + " | "
          + colored(f"Total: {scan_stats['total']}", "white"), end="")


    print("\nMost recent scanned hosts:")
    for scan_info in reversed(recent_scans):
        host_str, status = scan_info
        color = "green" if status == "Success" else "red"
        print(colored(f"{host_str} - {status}", color))


def show_results():
    """Display the scan results."""
    results_file = "results/scanned_hosts.txt"
    if not os.path.exists(results_file):
        print("[ERROR] No results found. Perform a scan first.")
        return

    with open(results_file, "r") as file:
        results = file.read()
        print("[INFO] Scan Results:\n")
        print(results)


def clear_results():
    """Clear the scan results file."""
    results_file = "results/scanned_hosts.txt"
    if os.path.exists(results_file):
        os.remove(results_file)
        print("[INFO] Results file cleared.")
    else:
        print("[INFO] No results file to clear.")
