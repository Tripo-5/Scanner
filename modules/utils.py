from globals import (
    global_hosts, global_live_hosts, global_scan_stats,
    pause_event, stop_event
)
import os
import csv
import random
import shutil
import time
from termcolor import colored

# Ensure required directories exist
os.makedirs("results", exist_ok=True)
os.makedirs("wordlists", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Log file for errors
error_log_file = "logs/errors.log"


def log_error(message):
    """
    Log errors to a log file for troubleshooting.

    :param message: Error message to log.
    """
    with open(error_log_file, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    print(colored(f"[ERROR] {message}", "red"))


def ensure_wordlists():
    """
    Ensure required wordlist files exist, create them if missing.
    """
    required_wordlists = {
        "wordlists/ssh_usernames.txt": ["root", "admin", "user"],
        "wordlists/ssh_passwords.txt": ["123456", "password", "admin"]
    }

    for file_path, default_values in required_wordlists.items():
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                file.write("\n".join(default_values) + "\n")
            print(colored(f"[INFO] Created default wordlist: {file_path}", "yellow"))


def ensure_valid_hosts():
    """
    Ensure the valid hosts file exists.
    """
    valid_hosts_file = "results/valid_hosts.txt"
    if not os.path.exists(valid_hosts_file):
        open(valid_hosts_file, "w").close()
        print(colored("[INFO] Created valid_hosts.txt file.", "yellow"))


def clear_all_chunks():
    """
    Remove all split CSV chunk files.
    """
    base_dir = "ip_ranges"
    if not os.path.exists(base_dir):
        print(colored("[ERROR] Base directory not found.", "red"))
        return

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if "Split-Chunk" in file:
                try:
                    os.remove(os.path.join(root, file))
                except Exception as e:
                    log_error(f"Failed to remove {file}: {e}")

    print(colored("[INFO] All chunk files cleared.", "green"))


def split_large_csvs(base_dir="ip_ranges", max_lines=50000):
    """
    Split large CSV files into smaller chunks.

    :param base_dir: Directory containing CSV files.
    :param max_lines: Maximum number of lines per chunk.
    """
    if not os.path.exists(base_dir):
        print(colored("[ERROR] Base directory does not exist.", "red"))
        return

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".csv") and "Split-Chunk" not in file:
                file_path = os.path.join(root, file)
                output_base = os.path.join(root, file.replace(".csv", "_Split-Chunk"))

                try:
                    with open(file_path, "r") as f:
                        reader = csv.reader(f)
                        lines = list(reader)

                    random.shuffle(lines)  # Shuffle IP ranges

                    chunk_number = 1
                    for i in range(0, len(lines), max_lines):
                        chunk_file = f"{output_base}{chunk_number}.csv"
                        with open(chunk_file, "w") as cf:
                            writer = csv.writer(cf)
                            writer.writerows(lines[i:i + max_lines])
                        chunk_number += 1

                    print(colored(f"[INFO] Processed {file} into {chunk_number - 1} chunks.", "green"))

                except Exception as e:
                    log_error(f"Failed to process {file}: {e}")


def load_tested_hosts():
    """
    Load previously tested live hosts from the results file.

    :return: List of tested live hosts.
    """
    live_hosts_file = "results/live_hosts.txt"
    if not os.path.exists(live_hosts_file):
        print(colored("[ERROR] No previously tested hosts found.", "red"))
        return []

    with open(live_hosts_file, "r") as file:
        tested_hosts = [line.strip() for line in file if line.strip()]

    print(colored(f"[INFO] Loaded {len(tested_hosts)} previously tested live hosts.", "green"))
    return tested_hosts
