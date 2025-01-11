import socket
import socks  # Import PySocks for SOCKS5 support
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm  # Progress bar library
import os

results = []

def send_tcp_probe(ip, proxy, port=22):
    """
    Sends a TCP probe to the specified IP and port using a SOCKS5 proxy.
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

def scan_host(ip, proxy):
    """
    Scans a single host for a response on port 22 using the provided proxy.
    """
    response = send_tcp_probe(ip, proxy)
    if response:
        return f"{ip}: {response.strip()}"
    return None

def scan_hosts(live_hosts, proxies):
    """
    Scans all live hosts using a list of proxies.
    """
    global results
    proxy_cycle = cycle(proxies)  # Cycles through the proxies
    print("[INFO] Starting scan of hosts...")

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_host = {executor.submit(scan_host, host, next(proxy_cycle)): host for host in live_hosts}
        for future in tqdm(future_to_host, desc="Scanning Hosts"):
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                print(f"[ERROR] Error scanning {future_to_host[future]}: {e}")

    with open("Banner_checks_complete.txt", "w") as result_file:
        result_file.write("\n".join(results))
    print(f"[INFO] Scan complete. Results saved to Banner_checks_complete.txt.")

def show_results():
    """
    Displays the results of the scans.
    """
    if os.path.exists("Banner_checks_complete.txt"):
        with open("Banner_checks_complete.txt", "r") as file:
            print(file.read())
    else:
        print("[INFO] No results found.")

def clear_results():
    """
    Clears the results file.
    """
    if os.path.exists("Banner_checks_complete.txt"):
        os.remove("Banner_checks_complete.txt")
        print("[INFO] Results file cleared.")
    else:
        print("[INFO] No results file to clear.")

