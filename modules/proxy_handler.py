from globals import global_scraped_proxies, global_tested_proxies, pause_event, stop_event
import socks
import socket
from tqdm import tqdm
import os
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def scrape_proxies():
    """
    Scrape proxies from the sources listed in proxy_sources.txt and save valid IP:Port pairs to unchecked_proxies.txt.
    """
    proxy_sources_file = "proxy_lists/proxy_sources.txt"
    unchecked_proxies_file = "proxy_lists/unchecked_proxies.txt"

    if not os.path.exists(proxy_sources_file):
        print(f"[ERROR] Proxy sources file not found: {proxy_sources_file}")
        return

    with open(proxy_sources_file, "r") as file:
        sources = [line.strip() for line in file if line.strip()]

    if not sources:
        print("[ERROR] No proxy sources found in proxy_sources.txt.")
        return

    print("[INFO] Scraping proxies from sources...")
    scraped_proxies = []

    proxy_pattern = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3}:\d+)")

    for source in tqdm(sources, desc="Scraping Sources"):
        # Check for stop or pause events
        if stop_event.is_set():
            print("[INFO] Scraping stopped.")
            break
        while pause_event.is_set():
            tqdm.write("[INFO] Scraping paused. Press F5 to resume.")
            time.sleep(0.5)

        try:
            response = requests.get(source, timeout=10)
            response.raise_for_status()

            proxies = proxy_pattern.findall(response.text)
            scraped_proxies.extend(proxies)
        except Exception as e:
            print(f"[ERROR] Failed to scrape from {source}: {e}")

    scraped_proxies = list(set(scraped_proxies))  # Deduplicate proxies
    with open(unchecked_proxies_file, "a") as file:
        for proxy in scraped_proxies:
            file.write(proxy + "\n")

    print(f"[INFO] Scraped {len(scraped_proxies)} valid proxies and saved to {unchecked_proxies_file}.")

def test_proxies(proxies):
    """
    Test the list of proxies concurrently and store the working ones in the global_tested_proxies variable.

    :param proxies: List of proxies to test
    :return: List of working proxies
    """
    global global_tested_proxies
    global_tested_proxies = []

    if not proxies:
        print("[ERROR] No proxies to test. Load proxies first.")
        return []

    print("[INFO] Testing proxies...")

    def test_and_store(proxy):
        try:
            proxy_host, proxy_port = proxy
            if test_single_proxy(proxy_host, int(proxy_port)):
                return proxy
        except ValueError:
            print(f"[ERROR] Invalid proxy format: {proxy}")
        return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_proxy = {executor.submit(test_and_store, proxy): proxy for proxy in proxies}
        for future in tqdm(as_completed(future_to_proxy), total=len(proxies), desc="Testing Proxies"):
            # Check for stop or pause events
            if stop_event.is_set():
                print("[INFO] Proxy testing stopped.")
                break
            while pause_event.is_set():
                tqdm.write("[INFO] Proxy testing paused. Press F5 to resume.")
                time.sleep(0.5)

            result = future.result()
            if result:
                global_tested_proxies.append(result)

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
        sock.settimeout(5)  # 5-second timeout for testing
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
