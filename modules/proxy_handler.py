import socks
import socket
import os
import requests
import re
import time
import threading
from tqdm import tqdm
from collections import deque
from globals import global_scraped_proxies, global_tested_proxies, pause_event, stop_event
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure proxy directory exists
proxy_lists_dir = "proxy_lists"
os.makedirs(proxy_lists_dir, exist_ok=True)

unchecked_proxies_file = os.path.join(proxy_lists_dir, "unchecked_proxies.txt")
checked_proxies_file = os.path.join(proxy_lists_dir, "checked_proxies.txt")
proxy_sources_file = os.path.join(proxy_lists_dir, "proxy_sources.txt")

# Ensure required files exist
for file_path in [unchecked_proxies_file, checked_proxies_file, proxy_sources_file]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("")

def load_proxies():
    """
    Load proxies from the unchecked proxies file into global_scraped_proxies.
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
    Scrape proxies from the sources listed in proxy_sources.txt and save valid IP:Port pairs.
    """
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
        try:
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            proxies = proxy_pattern.findall(response.text)
            scraped_proxies.extend(proxies)
        except Exception as e:
            print(f"[ERROR] Failed to scrape from {source}: {e}")

    scraped_proxies = list(set(scraped_proxies))  # Remove duplicates

    with open(unchecked_proxies_file, "a") as file:
        for proxy in scraped_proxies:
            file.write(proxy + "\n")

    print(f"[INFO] Scraped {len(scraped_proxies)} valid proxies and saved to {unchecked_proxies_file}.")

def test_proxies(proxies):
    """
    Test a list of proxies using multithreading.

    :param proxies: List of proxies to test (IP:Port format)
    """
    print("[INFO] Starting proxy testing...")

    # Counters for valid and invalid proxies
    valid_proxies = 0
    invalid_proxies = 0

    # Use ThreadPoolExecutor for concurrent proxy testing
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(test_single_proxy, proxy): proxy for proxy in proxies}

        # Use tqdm to show progress bar and update counters dynamically
        for future in tqdm(futures, desc="Testing Proxies", total=len(futures)):
            result = future.result()

            if result:
                valid_proxies += 1
                print(colored(f"[VALID] Proxy {futures[future]} works!", "green"))
            else:
                invalid_proxies += 1
                print(colored(f"[ERROR] Proxy {futures[future]} failed!", "red"))

            # Add the current proxy to the deque
            recent_proxies.append(futures[future])

            # Update the output with colored statistics and limited proxies
            print(f"\r{colored(f'Valid Proxies: {valid_proxies}', 'green')} | "
                  f"{colored(f'Invalid Proxies: {invalid_proxies}', 'red')}   "
                  f"{colored(f'Total: {valid_proxies + invalid_proxies}', 'white')}", end="")

            # Print the most recent proxies (up to the PRINT_LIMIT)
            print("\nMost recent proxies tested:")
            for proxy in reversed(recent_proxies):
                print(colored(f"{proxy}", "yellow"))

    print(f"\n[INFO] Proxy testing complete.")
    print(f"[INFO] Valid proxies: {valid_proxies}")
    print(f"[INFO] Invalid proxies: {invalid_proxies}")

    return valid_proxies, invalid_proxies


# Limit for the number of proxies printed in terminal
PRINT_LIMIT = 20

# Deque to store the most recent proxies tested
recent_proxies = deque(maxlen=PRINT_LIMIT)

def test_single_proxy(proxy):
    """
    Test a single proxy by attempting to connect to a test server.

    :param proxy: Proxy in IP:Port format
    :return: Boolean (True if successful, False if failed)
    """
    # Check if scan is paused or stopped
    while pause_event.is_set():
        time.sleep(0.5)

    if stop_event.is_set():
        print("[INFO] Stopping proxy tests.")
        return False

    try:
        proxy_host, proxy_port = proxy.split(":")
        proxy_port = int(proxy_port)

        # Set up SOCKS5 proxy using the provided proxy
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
        sock.settimeout(5)  # 5-second timeout for proxy connection
        sock.connect(("httpbin.org", 80))  # Test connection with a simple HTTP request
        sock.close()

        return True
    except (socket.error, socks.ProxyError) as e:
        return False

def save_working_proxies():
    """
    Save the working proxies to the checked proxies file.
    """
    with open(checked_proxies_file, "w") as file:
        for proxy in global_tested_proxies:
            file.write(":".join(proxy) + "\n")
    print(f"[INFO] Working proxies saved to {checked_proxies_file}.")

def load_checked_proxies():
    """
    Load previously tested proxies from checked_proxies.txt.
    """
    global global_tested_proxies

    if not os.path.exists(checked_proxies_file):
        print("[ERROR] No previously checked proxies found.")
        return []

    with open(checked_proxies_file, "r") as file:
        global_tested_proxies = [line.strip().split(":") for line in file if line.strip()]

    print(f"[INFO] Loaded {len(global_tested_proxies)} previously tested proxies.")
    return global_tested_proxies

def clear_proxies():
    """
    Clear both unchecked and checked proxy lists.
    """
    open(unchecked_proxies_file, "w").close()
    open(checked_proxies_file, "w").close()
    global_scraped_proxies.clear()
    global_tested_proxies.clear()
    print("[INFO] Proxy lists cleared.")

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
