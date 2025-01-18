from globals import global_hosts, global_live_hosts
import os
import ipaddress
from tqdm import tqdm
import random
import csv
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def load_hosts():
    """
    Load hosts from a file into the global_hosts variable.
    """
    global global_hosts
    file_path = input("Enter the path to the hosts file: ")
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return []

    with open(file_path, "r") as file:
        global_hosts = [line.strip() for line in file if line.strip()]
    print(f"[INFO] Loaded {len(global_hosts)} hosts from {file_path}.")
    return global_hosts

def load_ip_ranges():
    """
    Load IP ranges from CSV files within country-named folders in the ip_ranges directory,
    calculate all IPs within the ranges, and save them to global_hosts.
    Additionally, save the calculated IPs to a file.
    """
    global global_hosts

    base_dir = "ip_ranges"
    if not os.path.exists(base_dir):
        print(f"[ERROR] Base directory {base_dir} does not exist.")
        return []

    # List available countries
    countries = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not countries:
        print(f"[INFO] No country directories found in {base_dir}.")
        return []

    print("[INFO] Available countries:")
    for i, country in enumerate(countries, start=1):
        print(f"{i}. {country}")

    try:
        country_choice = int(input("Select a country by number: ")) - 1
        if country_choice < 0 or country_choice >= len(countries):
            print("[ERROR] Invalid selection.")
            return []
    except ValueError:
        print("[ERROR] Invalid input. Please enter a number.")
        return []

    selected_country = countries[country_choice]
    country_dir = os.path.join(base_dir, selected_country)

    # List available CSV files in the selected country folder
    csv_files = [f for f in os.listdir(country_dir) if f.endswith(".csv")]
    if not csv_files:
        print(f"[INFO] No CSV files found in {country_dir}.")
        return []

    print(f"[INFO] Available IP range files in {selected_country}:")
    for i, csv_file in enumerate(csv_files, start=1):
        print(f"{i}. {csv_file}")

    try:
        file_choice = int(input("Select a file by number: ")) - 1
        if file_choice < 0 or file_choice >= len(csv_files):
            print("[ERROR] Invalid selection.")
            return []
    except ValueError:
        print("[ERROR] Invalid input. Please enter a number.")
        return []

    selected_file = csv_files[file_choice]
    file_path = os.path.join(country_dir, selected_file)

    # Prepare output directory for calculated IPs
    ip_addresses_dir = os.path.join(country_dir, "ip_addresses")
    if not os.path.exists(ip_addresses_dir):
        os.makedirs(ip_addresses_dir)

    output_file = os.path.join(ip_addresses_dir, f"{selected_country}IPV4List.txt")

    # Process the selected file
    all_ips = []
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        for line in reader:
            if len(line) != 2:
                print(f"[ERROR] Invalid IP range format: {line}")
                continue
            try:
                start_ip = ipaddress.IPv4Address(line[0].strip())
                end_ip = ipaddress.IPv4Address(line[1].strip())

                if start_ip > end_ip:
                    print(f"[ERROR] Start IP {start_ip} is greater than End IP {end_ip}.")
                    continue

                current_ip = start_ip
                while current_ip <= end_ip:
                    all_ips.append(str(current_ip))
                    current_ip += 1

            except ValueError:
                print(f"[ERROR] Invalid IP range: {line}")

    random.shuffle(all_ips)  # Shuffle the IP list for randomness
    global_hosts = all_ips

    # Save the calculated IPs to a file
    with open(output_file, "w") as output:
        for ip in global_hosts:
            output.write(ip + "\n")

    print(f"[INFO] Loaded {len(global_hosts)} IPs from {file_path} and saved to {output_file}.")
    return global_hosts

# Lock for thread-safe operations
lock = threading.Lock()

# Function to test a single host
def test_single_host(host):
    """
    Test connectivity to a single host via hping3.

    :param host: Host to test.
    """
    try:
        # Encode a payload and split into chunks
        payload = "TestPayload"  # Example payload
        encoded_payload = payload.encode().hex()  # Hex-encode the payload
        chunk_size = len(encoded_payload) // 4
        chunks = [encoded_payload[i:i+chunk_size] for i in range(0, len(encoded_payload), chunk_size)]

        # Send each chunk as a separate packet
        for chunk in chunks:
            result = subprocess.run(
                ["hping3", "-S", host, "-p", "80", "--data", chunk, "-c", "1"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode != 0:
                raise RuntimeError(f"Chunk failed for host {host}")
        
        # If all chunks are sent successfully, add to global_live_hosts
        with lock:
            global_live_hosts.append(host)

    except Exception as e:
        print(f"[ERROR] Unexpected error testing host {host}: {e}")

# Function to test hosts with a thread limit
def test_hosts(hosts, proxies):
    """
    Test connectivity to hosts via hping3 using multithreading with a thread limit.

    :param hosts: List of hosts to test.
    :param proxies: List of proxies to use for testing (not used in hping3 test).
    :return: List of live hosts.
    """
    global global_live_hosts
    global_live_hosts = []  # Clear previous live hosts

    if not hosts:
        print("[ERROR] No hosts to test.")
        return []

    print("[INFO] Testing host connectivity via hping3 with a thread limit of 12...")
    
    # Use ThreadPoolExecutor with a maximum of 12 threads
    with ThreadPoolExecutor(max_workers=12) as executor:
        # Submit all host tests as tasks
        futures = {executor.submit(test_single_host, host): host for host in hosts}
        
        # Use tqdm to display progress
        for future in tqdm(as_completed(futures), total=len(futures), desc="Testing Hosts"):
            try:
                future.result()  # Ensure exceptions are raised
            except Exception as e:
                host = futures[future]
                print(f"[ERROR] Error testing host {host}: {e}")

    print(f"[INFO] Found {len(global_live_hosts)} live hosts.")
    return global_live_hosts
