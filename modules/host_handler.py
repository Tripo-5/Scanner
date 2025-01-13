
import socket
from tqdm import tqdm
import os
import ipaddress
import csv
import random

live_hosts = []
hosts = []

def load_hosts():
    """
    Load individual hosts from a text file.
    """
    global hosts
    hosts = []
    file_path = input("Enter the file path for hosts: ")
    if not file_path or not os.path.exists(file_path):
        print(f"[ERROR] File {file_path} does not exist.")
        return

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                hosts.append(line)
    print(f"[INFO] Loaded {len(hosts)} hosts from {file_path}.")

def load_ip_ranges(process_chunks=False):
    """
    Process IP ranges from raw CSV files or pre-processed chunks, split into smaller chunks if required,
    and load them into the global hosts list for testing/scanning.
    """
    global hosts
    base_dir = "ip_ranges"
    if not os.path.exists(base_dir):
        print(f"[ERROR] Directory {base_dir} not found. Please ensure it exists in the project folder.")
        return

    hosts = []
    for country in os.listdir(base_dir):
        country_dir = os.path.join(base_dir, country)
        if not os.path.isdir(country_dir):
            continue

        # Process either raw CSVs or already created chunks
        for file_name in os.listdir(country_dir):
            file_path = os.path.join(country_dir, file_name)
            if process_chunks and not file_name.startswith("chunk_"):
                continue  # Skip raw files if processing only chunks

            if not process_chunks and not file_name.endswith(".csv"):
                continue  # Skip chunks if processing only raw files

            with open(file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    line = line.strip()
                    if line:
                        hosts.append(line)

    print(f"[INFO] Loaded {len(hosts)} IPs from {'chunks' if process_chunks else 'raw CSV files'}.")

def split_large_csvs():
    """
    Split large IP range CSV files into manageable chunks for easier processing.
    """
    base_dir = "ip_ranges"
    if not os.path.exists(base_dir):
        print(f"[ERROR] Directory {base_dir} not found. Please ensure it exists in the project folder.")
        return

    for country in os.listdir(base_dir):
        country_dir = os.path.join(base_dir, country)
        if not os.path.isdir(country_dir):
            continue

        # Process each raw CSV in the directory
        for file_name in os.listdir(country_dir):
            file_path = os.path.join(country_dir, file_name)
            if not file_path.endswith('.csv'):
                continue

            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                ip_list = [row[0] for row in reader]

            random.shuffle(ip_list)
            chunk_size = 50000
            for i in range(0, len(ip_list), chunk_size):
                chunk = ip_list[i:i + chunk_size]
                output_file = os.path.join(country_dir, f"chunk_{i // chunk_size + 1}.txt")
                with open(output_file, 'w') as out_file:
                    out_file.write("\n".join(chunk))

            print(f"[INFO] Processed {file_name} into chunks of {chunk_size} IPs.")

def test_hosts():
    """
    Test hosts from the global hosts list.
    """
    global hosts, live_hosts
    if not hosts:
        print("[INFO] Hosts not loaded. Reloading hosts from 'results/valid_hosts/hosts.txt'...")
        load_hosts()

    if not hosts:
        print("[ERROR] No hosts available for testing.")
        return

    live_hosts = []
    print("[INFO] Testing hosts...")
    for host in tqdm(hosts, desc="Testing hosts"):
        try:
            socket.gethostbyname(host)
            live_hosts.append(host)
        except socket.error:
            continue

    with open("results/valid_hosts/live_hosts.txt", "w") as live_file:
        live_file.write("\n".join(live_hosts))
    print(f"[INFO] Testing complete. {len(live_hosts)} live hosts identified.")
