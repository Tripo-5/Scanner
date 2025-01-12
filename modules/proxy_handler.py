import os
import socks
import socket
from tqdm import tqdm
import requests
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# Base directory for proxy storage
PROXY_BASE_DIR = "proxy_ranges"
PROXY_TESTED_DIR = os.path.join(PROXY_BASE_DIR, "Tested")
PROXY_UNTESTED_DIR = os.path.join(PROXY_BASE_DIR, "Untested")
PROXY_TESTED_FILE = os.path.join(PROXY_TESTED_DIR, "live_proxies.txt")
PROXY_UNTESTED_FILE = os.path.join(PROXY_UNTESTED_DIR, "untested_proxies.txt")

# List of default proxy sources
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt",
    "https://github.com/TheSpeedX/PROXY-List/blob/master/socks5.txt",
    "https://sockslist.us/",
    "https://proxy-best.com/free-proxy-list/",
    "https://proxybros.com/free-proxy-list/socks5/",
    "https://github.com/proxifly/free-proxy-list",
    "https://www.socks-proxy.net/",
    "https://proxyscrape.com/free-proxy-list",
    "https://github.com/vakhov/fresh-proxy-list",
    "https://www.vpnside.com/proxy/list/",
    "https://proxycompass.com/free-proxy/",
    "https://netnut.io/free-proxy-list/",
    "https://hide.mn/en/proxy-list/",
]

working_proxies = []


def fetch_proxies():
    """
    Fetch proxies from multiple sources and save them to the untested directory.
    """
    proxies = set()
    headers = {'User-Agent': 'Mozilla/5.0'}
    for url in PROXY_SOURCES:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            for line in soup.get_text().splitlines():
                if re.match(r'\d+\.\d+\.\d+\.\d+:\d+', line.strip()):
                    proxies.add(line.strip())
        except requests.RequestException as e:
            print("Error fetching proxies from {}: {}".format(url, e))

    os.makedirs(PROXY_UNTESTED_DIR, exist_ok=True)
    with open(PROXY_UNTESTED_FILE, "w") as file:
        for proxy in proxies:
            file.write(proxy + "\n")
    print("[INFO] Saved {} untested proxies to {}".format(len(proxies), PROXY_UNTESTED_FILE))


def load_proxies():
    """
    Load proxies from the specified file or default to the untested proxy file.
    """
    global working_proxies
    file_path = input("Enter the proxy file path (leave empty to use default untested proxies): ").strip()
    if not file_path:
        print("[INFO] Using default untested proxies.")
        if not os.path.exists(PROXY_UNTESTED_FILE):
            print("[ERROR] No untested proxies found. Fetching new proxies...")
            fetch_proxies()
        file_path = PROXY_UNTESTED_FILE

    try:
        with open(file_path, 'r') as file:
            working_proxies = [line.strip().split(":") for line in file if line.strip()]
            print("[INFO] Loaded {} proxies from file.".format(len(working_proxies)))
    except FileNotFoundError:
        print("[ERROR] Proxy file not found: {}".format(file_path))


def test_proxies():
    """
    Test the loaded proxies for connectivity.
    """
    global working_proxies
    if not working_proxies:
        print("[ERROR] No proxies loaded. Please load proxies first.")
        return

    print("[INFO] Testing proxies...")
    tested_proxies = []
    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in working_proxies}
        for future in tqdm(as_completed(future_to_proxy), total=len(working_proxies), desc="Testing Proxies"):
            proxy = future_to_proxy[future]
            try:
                if future.result():
                    print("[INFO] Live proxy found: {}".format(":".join(proxy)))
                    tested_proxies.append(proxy)
            except Exception as e:
                print("[ERROR] Error testing proxy {}: {}".format(":".join(proxy), e))

    working_proxies = tested_proxies
    save_to_tested([":".join(proxy) for proxy in working_proxies])
    print("[INFO] {} working proxies saved to {}".format(len(working_proxies), PROXY_TESTED_FILE))


def test_proxy(proxy):
    """
    Test an individual proxy by attempting to connect to Google's public DNS.
    """
    proxy_host, proxy_port = proxy
    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, proxy_host, int(proxy_port))
        sock.settimeout(5)  # 5-second timeout for testing
        sock.connect(("8.8.8.8", 53))  # Connect to Google's public DNS
        sock.close()
        return True
    except (socket.timeout, OSError):
        return False


def save_to_tested(proxies):
    """
    Save live proxies to the tested directory.
    """
    os.makedirs(PROXY_TESTED_DIR, exist_ok=True)
    with open(PROXY_TESTED_FILE, "w") as file:
        for proxy in proxies:
            file.write(proxy + "\n")
    print("[INFO] Saved {} live proxies to {}".format(len(proxies), PROXY_TESTED_FILE))


if __name__ == "__main__":
    load_proxies()
    test_proxies()

