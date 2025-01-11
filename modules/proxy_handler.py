import socks
import socket
from tqdm import tqdm

working_proxies = []

def load_proxies():
    global working_proxies
    file_path = input("Enter the proxy file path: ")
    try:
        with open(file_path, 'r') as file:
            working_proxies = [line.strip().split(":") for line in file if line.strip()]
            print(f"[INFO] Loaded {len(working_proxies)} proxies from file.")
    except FileNotFoundError:
        print(f"[ERROR] Proxy file not found: {file_path}")

def test_proxies():
    global working_proxies
    if not working_proxies:
        print("[ERROR] No proxies loaded. Please load proxies first.")
        return

    print("[INFO] Testing proxies...")
    tested_proxies = [proxy for proxy in tqdm(working_proxies, desc="Testing Proxies") if test_proxy(proxy)]
    working_proxies = tested_proxies
    with open("live_proxies_tested.txt", "w") as file:
        for proxy in working_proxies:
            file.write(":".join(proxy) + "\n")
    print(f"[INFO] {len(working_proxies)} working proxies saved to live_proxies_tested.txt.")

def test_proxy(proxy):
    proxy_host, proxy_port = proxy
    try:
        sock = socks.socksocket()
        sock.set_proxy(socks.SOCKS5, proxy_host, int(proxy_port))
        sock.settimeout(2)  # 2-second timeout for testing
        sock.connect(("8.8.8.8", 53))  # Connect to Google's public DNS
        sock.close()
        return True
    except (socket.timeout, OSError):
        return False

