from globals import global_scraped_proxies, global_tested_proxies
import socks
import socket
from tqdm import tqdm
import os

# Create proxy_lists folder if it doesn't exist
proxy_lists_dir = "proxy_lists"
if not os.path.exists(proxy_lists_dir):
    os.makedirs(proxy_lists_dir)
    print(f"[INFO] Created directory: {proxy_lists_dir}")

unchecked_proxies_file = os.path.join(proxy_lists_dir, "unchecked_proxies.txt")
checked_proxies_file = os.path.join(proxy_lists_dir, "checked_proxies.txt")
proxy_sources_file = os.path.join(proxy_lists_dir, "proxy_sources.txt")

# Ensure necessary files exist
for file_path in [unchecked_proxies_file, checked_proxies_file, proxy_sources_file]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("")
        print(f"[INFO] Created file: {file_path}")

def load_proxies():
    """
    Load proxies from the unchecked proxies file and store them in the global_scraped_proxies variable.
    """
    global global_scraped_proxies
    if not os.path.exists(unchecked_proxies_file):
        print(f"[ERROR] Unchecked proxies file not found: {unchecked_proxies_file}")
        return []

    with open(unchecked_proxies_file, "r") as file:
        global_scraped_proxies = [line.strip().split(":") for line in file if line.strip()]
    print(f"[INFO] Loaded {len(global_scraped_proxies)} proxies from {unchecked_proxies_file}.")
    return global_scraped_proxies

def test_proxies(proxies):
    """
    Test the list of proxies and store the working ones in the global_tested_proxies variable.

    :param proxies: List of proxies to test
    :return: List of working proxies
    """
    global global_tested_proxies
    global_tested_proxies = []

    if not proxies:
        print("[ERROR] No proxies to test. Load proxies first.")
        return []

    print("[INFO] Testing proxies...")
    for proxy in tqdm(proxies, desc="Testing Proxies"):
        try:
            proxy_host, proxy_port = proxy
            if test_single_proxy(proxy_host, int(proxy_port)):
                global_tested_proxies.append(proxy)
        except ValueError:
            print(f"[ERROR] Invalid proxy format: {proxy}")

    print(f"[INFO] {len(global_tested_proxies)} working proxies found.")
    save_working_proxies()
    return global_tested_proxies

def test_single_proxy(proxy_host, proxy_port):
    """
    Test a single proxy by attempting to connect to a known endpoint.

    :param proxy_host: Proxy IP address
    :param proxy_port: Proxy port
    :return: True if the proxy works, False otherwise
    """
    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
        sock.settimeout(2)  # 2-second timeout for testing
        sock.connect(("8.8.8.8", 53))  # Connect to Google's public DNS
        sock.close()
        return True
    except (socket.timeout, OSError):
        return False

def save_working_proxies():
    """
    Save the working proxies to the checked proxies file for future use.
    """
    with open(checked_proxies_file, "w") as file:
        for proxy in global_tested_proxies:
            file.write(":".join(proxy) + "\n")
    print(f"[INFO] Working proxies saved to {checked_proxies_file}.")

def add_proxy_sources():
    """
    Add new proxy sources to the proxy_sources.txt file.
    """
    print("[INFO] Adding new proxy sources. Enter URLs (one per line). Type 'done' to finish.")
    new_sources = []
    while True:
        source = input("Enter proxy source URL: ").strip()
        if source.lower() == "done":
            break
        if source:
            new_sources.append(source)

    with open(proxy_sources_file, "a") as file:
        for source in new_sources:
            file.write(source + "\n")
    print(f"[INFO] Added {len(new_sources)} new proxy sources to {proxy_sources_file}.")
