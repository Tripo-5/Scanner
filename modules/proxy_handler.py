from globals import global_scraped_proxies, global_tested_proxies
import socks
import socket
from tqdm import tqdm
import os
import requests
import csv
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Create proxy_lists folder if it doesn't exist
proxy_lists_dir = "proxy_lists"
os.makedirs(proxy_lists_dir, exist_ok=True)

unchecked_proxies_file = os.path.join(proxy_lists_dir, "unchecked_proxies.txt")
checked_proxies_file = os.path.join(proxy_lists_dir, "checked_proxies.txt")
proxy_sources_file = os.path.join(proxy_lists_dir, "proxy_sources.txt")

# Ensure necessary files exist
for file_path in [unchecked_proxies_file, checked_proxies_file, proxy_sources_file]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("")

def load_proxies():
    """Load proxies from the unchecked proxies file."""
    global global_scraped_proxies
    if not os.path.exists(unchecked_proxies_file):
        return []

    with open(unchecked_proxies_file, "r") as file:
        global_scraped_proxies = [line.strip().split(":") for line in file if line.strip()]
    return global_scraped_proxies

def scrape_proxies():
    """Scrape proxies from the sources listed in proxy_sources.txt."""
    if not os.path.exists(proxy_sources_file):
        return

    with open(proxy_sources_file, "r") as file:
        sources = [line.strip() for line in file if line.strip()]

    if not sources:
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
        except Exception:
            pass

    scraped_proxies = list(set(scraped_proxies))
    with open(unchecked_proxies_file, "a") as file:
        for proxy in scraped_proxies:
            file.write(proxy + "\n")

def test_proxies(proxies):
    """Test the list of proxies concurrently."""
    global global_tested_proxies
    global_tested_proxies = []

    if not proxies:
        return []

    print("[INFO] Testing proxies...")

    def test_and_store(proxy):
        try:
            proxy_host, proxy_port = proxy
            if test_single_proxy(proxy_host, int(proxy_port)):
                return proxy
        except ValueError:
            pass
        return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_proxy = {executor.submit(test_and_store, proxy): proxy for proxy in proxies}
        for future in tqdm(as_completed(future_to_proxy), total=len(proxies), desc="Testing Proxies"):
            result = future.result()
            if result:
                global_tested_proxies.append(result)

    save_working_proxies()
    return global_tested_proxies

def test_single_proxy(proxy_host, proxy_port):
    """Test a single proxy by attempting to connect to a known endpoint."""
    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, proxy_host, proxy_port)
        sock.settimeout(5)
        sock.connect(("8.8.8.8", 53))
        sock.close()
        return True
    except:
        return False

def save_working_proxies():
    """Save the working proxies to the checked proxies file."""
    with open(checked_proxies_file, "w") as file:
        for proxy in global_tested_proxies:
            file.write(":".join(proxy) + "\n")

def load_checked_proxies():
    """Load previously tested proxies."""
    global global_tested_proxies
    if not os.path.exists(checked_proxies_file):
        return []

    with open(checked_proxies_file, "r") as file:
        global_tested_proxies = [line.strip().split(":") for line in file if line.strip()]
    return global_tested_proxies

def clear_proxies():
    """Clear all proxy files."""
    for file_path in [unchecked_proxies_file, checked_proxies_file]:
        with open(file_path, "w") as f:
            f.write("")
    global_scraped_proxies.clear()
    global_tested_proxies.clear()
