from main import global_scraped_proxies, global_tested_proxies
import socks
import socket
from tqdm import tqdm


def load_proxies():
    """
    Load proxies from a file and store them in the global_scraped_proxies variable.
    """
    global global_scraped_proxies
    file_path = input("Enter the proxy file path: ")
    if not file_path or not os.path.exists(file_path):
        print(f"[ERROR] Proxy file not found: {file_path}")
        return []

    with open(file_path, "r") as file:
        global_scraped_proxies = [line.strip().split(":") for line in file if line.strip()]
    print(f"[INFO] Loaded {len(global_scraped_proxies)} proxies from {file_path}.")
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
    Save the working proxies to a file for future use.
    """
    file_path = "results/working_proxies.txt"
    with open(file_path, "w") as file:
        for proxy in global_tested_proxies:
            file.write(":".join(proxy) + "\n")
    print(f"[INFO] Working proxies saved to {file_path}.")
