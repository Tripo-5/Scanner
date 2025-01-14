from main import global_live_hosts, global_tested_proxies
from tqdm import tqdm
import random
import socks
import socket

def send_tcp_probe(ip, proxy, port=22):
    """
    Send a TCP probe to a specific IP address and port using a proxy.

    :param ip: Target IP address
    :param proxy: Proxy details (host and port)
    :param port: Port to probe (default: 22)
    :return: Response data or None if failed
    """
    proxy_host, proxy_port = proxy
    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, proxy_host, int(proxy_port))
        sock.settimeout(0.8)  # 800ms timeout
        sock.connect((ip, port))

        sock.sendall(b"Hello\n")
        data = sock.recv(1024)
        sock.close()
        return data.decode('utf-8', errors='ignore')
    except (socket.timeout, OSError):
        return None

def scan_hosts(hosts, proxies):
    """
    Scan a list of hosts using available proxies.

    :param hosts: List of hosts to scan
    :param proxies: List of proxies to use for scanning
    """
    if not hosts:
        print("[ERROR] No hosts available for scanning.")
        return

    if not proxies:
        print("[ERROR] No proxies available for scanning.")
        return

    proxy_cycle = cycle(proxies)  # Cycle through proxies

    print("[INFO] Starting host scan...")
    results = []

    for host in tqdm(hosts, desc="Scanning Hosts"):
        proxy = next(proxy_cycle)
        try:
            response = send_tcp_probe(host, proxy)
            if response:
                results.append(f"{host}: {response.strip()}")
        except Exception as e:
            print(f"[ERROR] Error scanning host {host}: {e}")

    # Save scan results
    results_file = "results/scanned_hosts.txt"
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
