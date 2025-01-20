from globals import global_live_hosts, global_tested_proxies
from tqdm import tqdm
import socks
import socket
import os
import re
from itertools import cycle


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
    except (socket.error, socks.ProxyError, socks.GeneralProxyError) as e:
        return None

def scan_hosts():
    """
    Scan hosts in global_live_hosts using proxies from global_tested_proxies.
    Perform a banner check on port 22.
    """
    if not global_live_hosts:
        print("[ERROR] No live hosts available for scanning.")
        return

    if not global_tested_proxies:
        print("[ERROR] No tested proxies available for scanning.")
        return

    proxy_cycle = cycle(global_tested_proxies)  # Cycle through proxies
    print("[INFO] Starting host scan...")
    results = []

    for host in tqdm(global_live_hosts, desc="Scanning Hosts"):
        proxy = next(proxy_cycle)
        try:
            banner = send_tcp_probe(host, proxy)
            if banner:
                results.append(f"{host}: {banner}")
        except Exception as e:
            print(f"[ERROR] Error scanning host {host}: {e}")

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
