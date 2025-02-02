from globals import global_scraped_proxies, global_tested_proxies, proxy_stats, pause_event, stop_event
import socks
import socket
import os
import requests
import re
import time
import threading
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from termcolor import colored
from main import display_statistics  # Import the function from main.py
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

# Function to print live proxy statistics in the menu
def update_proxy_stats():
    proxy_stats["remaining"] = proxy_stats["total"] - (proxy_stats["valid"] + proxy_stats["dead"])

def load_proxies():
    """Load proxies from the unchecked proxies file into global_scraped_proxies."""
    global global_scraped_proxies
    if not os.path.exists(unchecked_proxies_file):
        print(f"[ERROR] Unchecked proxies file not found: {unchecked_proxies_file}")
        return []

    with open(unchecked_proxies_file, "r") as file:
        global_scraped_proxies = [line.strip() for line in file if line.strip()]

    print(f"[INFO] Loaded {len(global_scraped_proxies)} proxies from {unchecked_proxies_file}.")
    return global_scraped_proxies


def scrape_proxies():
    """Scrape proxies from sources and save valid IP:Port pairs."""
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


# Test Proxies (Live Stats Only - No Detailed Output)
def test_proxies(proxies):
    """
    Test a list of proxies using multithreading and update statistics in real time.
    """
    global proxy_stats

    if not proxies:
        print("[ERROR] No proxies to test. Load proxies first.")
        return []

    proxy_stats["total"] = len(proxies)
    proxy_stats["valid"] = 0
    proxy_stats["dead"] = 0
    proxy_stats["remaining"] = len(proxies)

    print("[INFO] Starting proxy testing...")

    with ThreadPoolExecutor(max_workers=30) as executor:  # Reduce max workers to prevent overload
        futures = {executor.submit(test_single_proxy, proxy): proxy for proxy in proxies}

        for future in tqdm(as_completed(futures), total=len(futures), desc="Testing Proxies"):
            if stop_event.is_set():
                print("[INFO] Stopping proxy testing.")
                break  # Exit if stop is triggered

            while pause_event.is_set():  # Handle pausing properly
                time.sleep(0.5)

            try:
                proxy = futures[future]
                result = future.result(timeout=10)  # Ensure proxy doesn't block forever

                if result:
                    proxy_stats["valid"] += 1
                else:
                    proxy_stats["dead"] += 1

                proxy_stats["remaining"] -= 1
                display_statistics()  # Refresh menu dynamically

            except Exception as e:
                print(colored(f"[ERROR] Proxy test failed: {e}", "red"))
                proxy_stats["dead"] += 1
                proxy_stats["remaining"] -= 1
                display_statistics()

    print(f"\n[INFO] Proxy testing complete.")
    print(f"[INFO] Valid proxies: {proxy_stats['valid']}")
    print(f"[INFO] Dead proxies: {proxy_stats['dead']}")

    
    def update_status():
        """ Update statistics live while scanning """
        proxy_stats["remaining"] = proxy_stats["total"] - (proxy_stats["valid"] + proxy_stats["dead"])
    
    # Multithreading to test proxies
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(test_single_proxy, proxy): proxy for proxy in proxies}

        for future in tqdm(as_completed(futures), total=len(futures), desc="Testing Proxies"):
            proxy = futures[future]
            result = future.result()

            if result:
                proxy_stats["valid"] += 1  # Update valid proxies count
            else:
                proxy_stats["dead"] += 1  # Update dead proxies count

            update_status()  # Refresh remaining count

    print(f"\n[INFO] Proxy testing complete. Valid: {proxy_stats['valid']} | Dead: {proxy_stats['dead']}")
    return global_tested_proxies  # Return list of working proxies
    
    def background_testing():
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(test_single_proxy, proxy): proxy for proxy in proxies}

            for future in tqdm(as_completed(futures), total=len(futures), desc="Testing Proxies"):
                proxy = futures[future]
                result = future.result()

                if result:
                    proxy_stats["valid"] += 1
                    recent_proxies.append([proxy, "Valid"])
                else:
                    proxy_stats["dead"] += 1
                    recent_proxies.append([proxy, "Dead"])

                proxy_stats["remaining"] -= 1

                # Update status dynamically
                print_status()

    # Start the proxy test in the background
    testing_thread = threading.Thread(target=background_testing, daemon=True)
    testing_thread.start()


def print_status():
    """Update the terminal display dynamically with counters."""
    print("\r{} | {} | {} | {}".format(
        colored(f"Valid Proxies: {proxy_stats['valid']}", "green"),
        colored(f"Invalid Proxies: {proxy_stats['dead']}", "red"),
        colored(f"Remaining: {proxy_stats['remaining']}", "yellow"),
        colored(f"Total: {proxy_stats['total']}", "white")
    ), end="")


    print("\nMost recent proxies tested:")
    for proxy_info in reversed(recent_proxies):
        proxy_str, status = proxy_info
        color = "green" if status == "Valid" else "red"
        print(colored(f"{proxy_str} - {status}", color))


# Test Single Proxy (No Print Output)
def test_single_proxy(proxy):
    """
    Test a single proxy by attempting to connect to a test server.

    :param proxy: Proxy in IP:Port format
    :return: Boolean (True if successful, False if failed)
    """
    while pause_event.is_set():
        time.sleep(0.5)

    if stop_event.is_set():
        return False

    try:
        # Ensure proxy is in the correct format (IP:PORT)
        if isinstance(proxy, list):
            proxy = ":".join(proxy)

        proxy_host, proxy_port = proxy.split(":")
        proxy_port = int(proxy_port)

        if not (0 <= proxy_port <= 65535):
            print(colored(f"[ERROR] Invalid proxy port: {proxy_port}", "red"))
            return False

        # Set up SOCKS5 proxy using the provided proxy
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
        sock.settimeout(5)  # Ensure timeout to prevent freezing

        try:
            sock.connect(("httpbin.org", 80))  # Test connection
        except socket.timeout:
            return False  # Skip if timeout occurs

        sock.close()
        return True

    except (socket.error, socks.ProxyError) as e:
        return False

def save_working_proxies():
    """Save the working proxies to the checked proxies file."""
    with open(checked_proxies_file, "w") as file:
        for proxy in global_tested_proxies:
            file.write(f"{proxy}\n")
    print(f"[INFO] Working proxies saved to {checked_proxies_file}.")


def load_checked_proxies():
    """Load previously tested proxies from checked_proxies.txt."""
    global global_tested_proxies

    if not os.path.exists(checked_proxies_file):
        print("[ERROR] No previously checked proxies found.")
        return []

    with open(checked_proxies_file, "r") as file:
        global_tested_proxies = [line.strip() for line in file if line.strip()]

    print(f"[INFO] Loaded {len(global_tested_proxies)} previously tested proxies.")
    return global_tested_proxies


def clear_proxies():
    """Clear both unchecked and checked proxy lists."""
    open(unchecked_proxies_file, "w").close()
    open(checked_proxies_file, "w").close()
    global_scraped_proxies.clear()
    global_tested_proxies.clear()
    print("[INFO] Proxy lists cleared.")


def add_proxy_sources():
    """Add new proxy sources to the proxy_sources.txt file."""
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
