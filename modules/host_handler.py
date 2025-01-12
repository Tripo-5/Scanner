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

def load_ip_ranges():
    """
    Process IP ranges from a CSV file, split them into chunks of 50,000 IPs per file,
    randomize them, and save as individual text files in the respective country folder.
    """
    base_dir = "ip_ranges"  # Directory containing the country folders

    if not os.path.exists(base_dir):
        print(f"[ERROR] Directory {base_dir} not found. Please ensure it exists in the project folder.")
        return

    # List available countries (subfolders in the base_dir)
    countries = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not countries:
        print(f"[ERROR] No country directories found in {base_dir}.")
        return

    print("\n[ Country Selection Menu ]")
    for idx, country in enumerate(countries, 1):
        print(f"{idx}.) {country}")
    print(f"{len(countries) + 1}.) Exit to Main Menu")

    country_choice = input("Select a country by number: ")
    try:
        country_idx = int(country_choice) - 1
        if country_idx == len(countries):  # Exit option
            return
        selected_country = countries[country_idx]
        print(f"[INFO] Selected country: {selected_country}")
    except (IndexError, ValueError):
        print("[ERROR] Invalid selection.")
        return

    country_dir = os.path.join(base_dir, selected_country)

    # List CSV files in the selected country folder
    csv_files = [f for f in os.listdir(country_dir) if os.path.isfile(os.path.join(country_dir, f)) and f.endswith('.csv')]
    if not csv_files:
        print(f"[ERROR] No CSV files found in {country_dir}.")
        return

    print("\n[ CSV Selection Menu ]")
    for idx, csv_file in enumerate(csv_files, 1):
        print(f"{idx}.) {csv_file}")
    print(f"{len(csv_files) + 1}.) Exit to Main Menu")

    csv_choice = input("Select a CSV file by number: ")
    try:
        csv_idx = int(csv_choice) - 1
        if csv_idx == len(csv_files):  # Exit option
            return
        selected_csv_file = csv_files[csv_idx]
        print(f"[INFO] Selected CSV file: {selected_csv_file}")
    except (IndexError, ValueError):
        print("[ERROR] Invalid selection.")
        return

    csv_file_path = os.path.join(country_dir, selected_csv_file)

    # Detect or specify delimiter
    delimiter = input("Enter the CSV delimiter (default: ','): ") or ","

    # Generate chunked files in the country folder
    try:
        all_ips = []

        print(f"[DEBUG] Processing file: {csv_file_path} with delimiter: '{delimiter}'")
        with open(csv_file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=delimiter)
            for row in csv_reader:
                if len(row) != 2:
                    print(f"[ERROR] Invalid range format: {row}")
                    continue
                start_ip, end_ip = row
                try:
                    start = ipaddress.IPv4Address(start_ip.strip())
                    end = ipaddress.IPv4Address(end_ip.strip())
                    if start > end:
                        print(f"[ERROR] Invalid range: {start_ip} - {end_ip}")
                        continue

                    # Expand range into individual IPs and add to all_ips
                    for ip in range(int(start), int(end) + 1):
                        all_ips.append(str(ipaddress.IPv4Address(ip)))

                except ValueError as e:
                    print(f"[ERROR] Invalid IP range {start_ip} - {end_ip}: {e}")

        if not all_ips:
            print(f"[ERROR] No valid IPs found in {csv_file_path}.")
            return

        # Randomize all IPs before chunking
        random.shuffle(all_ips)

        # Save randomized IPs into chunks of 50,000 lines
        chunk_counter = 1
        for i in range(0, len(all_ips), 50000):
            chunk_filename = os.path.join(country_dir, f"{selected_csv_file.split('.')[0]}Split-Chunk{chunk_counter}.txt")
            if os.path.exists(chunk_filename):
                print(f"[INFO] Chunk file already exists: {chunk_filename}. Skipping generation.")
                continue
            print(f"[INFO] Creating chunk file: {chunk_filename}")
            with open(chunk_filename, 'w') as chunk_file:
                chunk_file.writelines(f"{ip}\n" for ip in all_ips[i:i + 50000])
            chunk_counter += 1

        print(f"[INFO] Generated {chunk_counter - 1} chunk files from {selected_csv_file}.")
    except FileNotFoundError:
        print(f"[ERROR] File {selected_csv_file} not found.")
    except csv.Error as e:
        print(f"[ERROR] CSV processing error: {e}")
    except Exception as e:
        print(f"[ERROR] Failed to process {csv_file_path}: {e}")
import socket
from tqdm import tqdm

live_hosts = []

def test_hosts():
    """
    Test connectivity for hosts listed in the chunked files.
    """
    global live_hosts
    live_hosts = []  # Clear any previously detected live hosts

    base_dir = "ip_ranges"  # Directory containing the country folders
    if not os.path.exists(base_dir):
        print(f"[ERROR] Directory {base_dir} not found. Please ensure it exists in the project folder.")
        return

    # List available countries (subfolders in the base_dir)
    countries = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not countries:
        print(f"[ERROR] No country directories found in {base_dir}.")
        return

    print("\n[ Country Selection Menu ]")
    for idx, country in enumerate(countries, 1):
        print(f"{idx}.) {country}")
    print(f"{len(countries) + 1}.) Exit to Main Menu")

    country_choice = input("Select a country by number: ")
    try:
        country_idx = int(country_choice) - 1
        if country_idx == len(countries):  # Exit option
            return
        selected_country = countries[country_idx]
        print(f"[INFO] Selected country: {selected_country}")
    except (IndexError, ValueError):
        print("[ERROR] Invalid selection.")
        return

    country_dir = os.path.join(base_dir, selected_country)

    # List chunk files in the selected country folder
    chunk_files = [f for f in os.listdir(country_dir) if os.path.isfile(os.path.join(country_dir, f)) and f.endswith('.txt') and "Split-Chunk" in f]
    if not chunk_files:
        print(f"[ERROR] No chunk files found in {country_dir}. Please generate chunks first.")
        return

    print("\n[ Chunk File Selection Menu ]")
    for idx, chunk_file in enumerate(chunk_files, 1):
        print(f"{idx}.) {chunk_file}")
    print(f"{len(chunk_files) + 1}.) Test All Chunks")
    print(f"{len(chunk_files) + 2}.) Exit to Main Menu")

    chunk_choice = input("Select a chunk file by number: ")
    try:
        chunk_idx = int(chunk_choice) - 1
        if chunk_idx == len(chunk_files):  # Test all chunks
            selected_chunks = chunk_files
            print("[INFO] Testing all chunks.")
        elif chunk_idx == len(chunk_files) + 1:  # Exit option
            return
        else:
            selected_chunks = [chunk_files[chunk_idx]]
            print(f"[INFO] Selected chunk file: {selected_chunks[0]}")
    except (IndexError, ValueError):
        print("[ERROR] Invalid selection.")
        return

    # Test connectivity for IPs in the selected chunk(s)
    for chunk_file in selected_chunks:
        chunk_path = os.path.join(country_dir, chunk_file)
        print(f"[INFO] Testing connectivity for hosts in: {chunk_file}")

        with open(chunk_path, 'r') as file:
            hosts = [line.strip() for line in file if line.strip()]

        for host in tqdm(hosts, desc=f"Testing {chunk_file}"):
            try:
                with socket.create_connection((host, 22), timeout=2):
                    live_hosts.append(host)
            except (socket.timeout, OSError):
                pass

    # Save live hosts to a file
    if live_hosts:
        live_hosts_file = os.path.join(country_dir, "Live_Hosts.txt")
        with open(live_hosts_file, 'w') as file:
            file.writelines(f"{host}\n" for host in live_hosts)
        print(f"[INFO] Detected {len(live_hosts)} live hosts. Saved to {live_hosts_file}.")
    else:
        print("[INFO] No live hosts detected.")

