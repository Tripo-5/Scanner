from globals import global_hosts, global_live_hosts
import os
import csv


def clear_all_chunks():
    """
    Clear all chunk files from all countries in the ip_ranges directory.
    """
    base_dir = "ip_ranges"  # Directory containing the country folders

    if not os.path.exists(base_dir):
        print(f"[ERROR] Directory {base_dir} not found. Please ensure it exists.")
        return

    countries = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not countries:
        print(f"[INFO] No country directories found in {base_dir}.")
        return

    for country in countries:
        country_dir = os.path.join(base_dir, country)
        chunk_files = [f for f in os.listdir(country_dir) if f.startswith("Split-Chunk") and f.endswith(".txt")]

        for chunk_file in chunk_files:
            chunk_path = os.path.join(country_dir, chunk_file)
            try:
                os.remove(chunk_path)
                print(f"[INFO] Removed chunk file: {chunk_path}")
            except Exception as e:
                print(f"[ERROR] Failed to remove {chunk_path}: {e}")

    print("[INFO] All chunk files have been cleared.")


def split_large_csvs(base_dir, max_lines):
    """
    Split large CSV files into smaller chunks based on the maximum number of lines.

    :param base_dir: Base directory containing the CSV files.
    :param max_lines: Maximum number of lines per chunk.
    """
    if not os.path.exists(base_dir):
        print(f"[ERROR] Directory {base_dir} not found.")
        return

    countries = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    if not countries:
        print(f"[INFO] No country directories found in {base_dir}.")
        return

    for country in countries:
        country_dir = os.path.join(base_dir, country)
        csv_files = [f for f in os.listdir(country_dir) if f.endswith(".csv")]

        for csv_file in csv_files:
            csv_path = os.path.join(country_dir, csv_file)
            print(f"[INFO] Processing file: {csv_path}")

            try:
                with open(csv_path, "r") as file:
                    reader = csv.reader(file)
                    lines = list(reader)

                for i in range(0, len(lines), max_lines):
                    chunk = lines[i:i + max_lines]
                    chunk_filename = f"{os.path.splitext(csv_file)[0]}_Split-Chunk{i // max_lines + 1}.csv"
                    chunk_path = os.path.join(country_dir, chunk_filename)

                    with open(chunk_path, "w", newline="") as chunk_file:
                        writer = csv.writer(chunk_file)
                        writer.writerows(chunk)

                    print(f"[INFO] Created chunk file: {chunk_path}")

            except Exception as e:
                print(f"[ERROR] Failed to split {csv_file}: {e}")



def ensure_wordlists():
    """
    Ensure wordlists are available in the required directory.
    """
    wordlist_dir = "wordlists"
    if not os.path.exists(wordlist_dir):
        os.makedirs(wordlist_dir)
        print(f"[INFO] Created missing directory: {wordlist_dir}")

    required_files = ["usernames.txt", "passwords.txt"]
    for file_name in required_files:
        file_path = os.path.join(wordlist_dir, file_name)
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                file.write("# Add your entries here\n")
            print(f"[INFO] Created placeholder file: {file_path}")


def ensure_valid_hosts():
    """
    Ensure valid hosts are written to a results file.
    """
    global global_live_hosts

    if not global_live_hosts:
        print("[INFO] No live hosts found in memory.")
        return

    results_dir = "results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        print(f"[INFO] Created missing directory: {results_dir}")

    valid_hosts_file = os.path.join(results_dir, "valid_hosts.txt")
    with open(valid_hosts_file, "w") as file:
        for host in global_live_hosts:
            file.write(f"{host}\n")

    print(f"[INFO] Live hosts saved to {valid_hosts_file}.")

def send_tcp_probe(ip, proxy, port=22, max_retries=3):
    """
    Perform a banner grab on the given IP and port using a SOCKS5 proxy.

    :param ip: Target IP address
    :param proxy: Proxy details (host, port)
    :param port: Target port (default: 22)
    :param max_retries: Number of retry attempts if a proxy fails
    :return: Banner string if successful, None otherwise
    """
    proxy_host, proxy_port = proxy
    attempt = 0

    while attempt < max_retries:
        try:
            print(colored(f"[INFO] Probing {ip} via {proxy_host}:{proxy_port}", "yellow"))

            # Set up SOCKS5 proxy
            sock = socks.socksocket()
            sock.set_proxy(socks.SOCKS5, proxy_host, int(proxy_port))
            sock.settimeout(5)  # Set a 5-second timeout

            # Connect to SSH port
            sock.connect((ip, port))
            sock.sendall(b"\n")  # Send a newline to trigger banner response

            # Receive banner
            banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
            sock.close()

            if banner:
                print(colored(f"[VALID] {ip} Banner: {banner}", "green"))
                return banner

        except (socket.error, socks.ProxyError, socks.GeneralProxyError) as e:
            print(colored(f"[ERROR] Proxy failed for {ip} via {proxy_host}:{proxy_port} - {e}", "red"))

        # Retry with exponential backoff
        attempt += 1
        wait_time = attempt * 2
        print(colored(f"[INFO] Retrying ({attempt}/{max_retries}) in {wait_time} seconds...", "cyan"))
        time.sleep(wait_time)

    print(colored(f"[DEAD] {ip} is unreachable after {max_retries} attempts.", "red"))
    return None
