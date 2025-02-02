from globals import global_scraped_proxies, global_tested_proxies, pause_event, stop_event
import socks
import socket
import os
import requests
import re
import time
import threading
from tqdm import tqdm
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
    
    :param proxies: List of proxies in IP:Port format
    """
    print("[INFO] Starting proxy testing...")
    results = []

    # Ensure that the threads pause when Tor is being renewed
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(test_single_proxy, proxy): proxy for proxy in proxies}

        for future in tqdm(futures, desc="Testing Proxies", total=len(futures)):
            # Handle pause during Tor renewal
            while pause_event.is_set():
                time.sleep(0.5)
            # Check for stop event to gracefully terminate
            if stop_event.is_set():
                print("[INFO] Stopping proxy tests.")
                break
            future.result()  # Ensure any exceptions are raised and handled
    print("[INFO] Proxy testing complete.")

def test_single_proxy(proxy, test_url="http://example.com"):
    """
    Test a single proxy by attempting to access a URL.
    
    :param proxy: Proxy in IP:Port format
    :param test_url: URL to test the proxy with
    """
    proxy_host, proxy_port = proxy.split(":")
    proxy_port = int(proxy_port)
    
    # Check if the scanning is paused or stopped
    while pause_event.is_set():
        time.sleep(0.5)

    if stop_event.is_set():
        print("[INFO] Stopping proxy testing.")
        return

    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
        sock.settimeout(5)  # 5-second timeout for proxy connection
        sock.connect((test_url, 80))  # Connecting to the test URL
        sock.close()
        print(colored(f"[VALID] Proxy {proxy} works!", "green"))
        return True
    except (socket.error, socks.ProxyError) as e:
        print(colored(f"[ERROR] Proxy {proxy} failed: {e}", "red"))
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
