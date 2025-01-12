import os
import csv

def show_results():
    if os.path.exists("Banner_checks_complete.txt"):
        with open("Banner_checks_complete.txt", "r") as file:
            print(file.read())
    else:
        print("[INFO] No results found.")

def clear_results():
    if os.path.exists("Banner_checks_complete.txt"):
        os.remove("Banner_checks_complete.txt")
        print("[INFO] Results cleared.")

def show_valid():
    if os.path.exists("cracked.txt"):
        with open("cracked.txt", "r") as file:
            print(file.read())
    else:
        print("[INFO] No valid credentials found.")

def clear_all_chunks():
    """
    Clear all chunk files from all countries in the ip_ranges directory.
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

    for country in countries:
        country_dir = os.path.join(base_dir, country)
        chunk_files = [f for f in os.listdir(country_dir) if f.endswith(".csv") and "Chunk" in f]

        for chunk_file in chunk_files:
            chunk_path = os.path.join(country_dir, chunk_file)
            try:
                os.remove(chunk_path)
                print(f"[INFO] Removed chunk file: {chunk_path}")
            except Exception as e:
                print(f"[ERROR] Failed to remove {chunk_path}: {e}")

    print(f"[INFO] All chunk files have been cleared.")

def split_large_csvs(base_dir="/SSH/ip_ranges", max_lines=1000):
    """
    Split large CSV files into smaller chunks, limiting each chunk to `max_lines`.

    Args:
        base_dir (str): Base directory containing country subfolders with CSV files.
        max_lines (int): Maximum number of lines per chunk.
    """
    if not os.path.exists(base_dir):
        print(f"[ERROR] Directory '{base_dir}' not found.")
        return

    # Iterate through each country's folder
    for country in os.listdir(base_dir):
        country_dir = os.path.join(base_dir, country)
        if not os.path.isdir(country_dir):
            continue

        # Find CSV files in the country folder
        csv_files = [f for f in os.listdir(country_dir) if f.endswith(".csv") and "Chunk" not in f]
        if not csv_files:
            print(f"[INFO] No large CSV files to process in '{country_dir}'.")
            continue

        for csv_file in csv_files:
            csv_path = os.path.join(country_dir, csv_file)
            base_name = os.path.splitext(csv_file)[0]

            # Split the CSV file into chunks
            try:
                with open(csv_path, 'r') as input_csv:
                    csv_reader = csv.reader(input_csv)
                    headers = next(csv_reader, None)  # Capture headers if present
                    chunk = []
                    chunk_count = 0

                    for line_num, row in enumerate(csv_reader, start=1):
                        chunk.append(row)
                        if line_num % max_lines == 0:
                            chunk_count += 1
                            output_file = os.path.join(
                                country_dir, f"{base_name}Chunk{chunk_count}.csv"
                            )
                            write_chunk(output_file, chunk, headers)
                            chunk = []

                    # Write the remaining rows to the last chunk
                    if chunk:
                        chunk_count += 1
                        output_file = os.path.join(
                            country_dir, f"{base_name}Chunk{chunk_count}.csv"
                        )
                        write_chunk(output_file, chunk, headers)

                    print(
                        f"[INFO] Split '{csv_file}' into {chunk_count} chunks in '{country_dir}'."
                    )
            except FileNotFoundError:
                print(f"[ERROR] File '{csv_path}' not found.")
            except Exception as e:
                print(f"[ERROR] Failed to split '{csv_file}': {e}")

def write_chunk(output_file, chunk, headers=None):
    """
    Write a chunk of rows to a CSV file.

    Args:
        output_file (str): Path to the output chunk file.
        chunk (list): List of rows to write.
        headers (list): Optional headers for the CSV file.
    """
    try:
        with open(output_file, 'w', newline='') as chunk_file:
            csv_writer = csv.writer(chunk_file)
            if headers:
                csv_writer.writerow(headers)
            csv_writer.writerows(chunk)
        print(f"[INFO] Created chunk: {output_file}")
    except Exception as e:
        print(f"[ERROR] Failed to write chunk '{output_file}': {e}")

def ensure_wordlists():
    """Ensure default wordlists exist in the 'wordlists' directory."""
    wordlist_dir = "wordlists"
    os.makedirs(wordlist_dir, exist_ok=True)

    username_file = os.path.join(wordlist_dir, "ssh_usernames.txt")
    password_file = os.path.join(wordlist_dir, "ssh_passwords.txt")

    if not os.path.exists(username_file):
        print(f"[INFO] Creating default username wordlist at {username_file}.")
        with open(username_file, "w") as uf:
            uf.write("root\nadmin\nuser\n")

    if not os.path.exists(password_file):
        print(f"[INFO] Creating default password wordlist at {password_file}.")
        with open(password_file, "w") as pf:
            pf.write("1234\nadmin\npassword\n")

def ensure_valid_hosts():
    """Check if valid hosts exist in 'results/valid_hosts'."""
    valid_hosts_dir = "results/valid_hosts"
    if not os.path.exists(valid_hosts_dir) or not any(f.endswith(".txt") for f in os.listdir(valid_hosts_dir)):
        print("[ERROR] No valid SSH servers found in 'results/valid_hosts'. Please run the scanning process first.")
        return False
    return True
