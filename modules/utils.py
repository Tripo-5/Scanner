import os

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
        chunk_files = [f for f in os.listdir(country_dir) if f.endswith(".txt") and "Split-Chunk" in f]

        for chunk_file in chunk_files:
            chunk_path = os.path.join(country_dir, chunk_file)
            try:
                os.remove(chunk_path)
                print(f"[INFO] Removed chunk file: {chunk_path}")
            except Exception as e:
                print(f"[ERROR] Failed to remove {chunk_path}: {e}")

    print(f"[INFO] All chunk files have been cleared.")

