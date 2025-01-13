
import os
from modules.proxy_handler import load_proxies, test_proxies
from modules.host_handler import load_hosts, load_ip_ranges, test_hosts
from modules.scanner import scan_hosts, show_results, clear_results
from modules.exploit import identify_vulnerable_hosts, exploit_vulnerable_hosts
from modules.utils import clear_all_chunks, split_large_csvs, ensure_wordlists, ensure_valid_hosts
from modules.bruteforce import load_wordlists, bruteforce_ssh

def ensure_environment():
    """
    Ensure that all required directories and files are in place.
    """
    required_directories = [
        "results",
        "results/valid_logins",
        "results/valid_hosts",
        "wordlists",
        "wordlists/ssh",
        "ip_ranges",
    ]
    required_files = [
        "Banner_checks_complete.txt",
        "live_proxies_tested.txt",
    ]

    for directory in required_directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"[INFO] Created missing directory: {directory}")

    for file in required_files:
        if not os.path.exists(file):
            with open(file, "w") as f:
                pass  # Create an empty file
            print(f"[INFO] Created missing file: {file}")

def main_menu():
    while True:
        try:
            print("\n[ Main Menu ]")
            print("1.) Load Proxies")
            print("2.) Test Proxies")
            print("3.) Load Hosts")
            print("4.) Load IP Ranges")
            print("5.) Test Hosts")
            print("6.) Scan Hosts")
            print("7.) Show Results")
            print("8.) Clear Results")
            print("9.) Identify Vulnerabilities")
            print("10.) Exploit Vulnerable Hosts")
            print("11.) Clear All Chunks")
            print("12.) Split Large CSVs")
            print("13.) Bruteforce SSH")
            print("14.) Exit")

            choice = input("Enter your choice: ").strip()

            if choice == "1":
                load_proxies()
            elif choice == "2":
                test_proxies()
            elif choice == "3":
                load_hosts()
            elif choice == "4":
                load_ip_ranges()
            elif choice == "5":
                test_hosts()
            elif choice == "6":
                scan_hosts()
            elif choice == "7":
                show_results()
            elif choice == "8":
                clear_results()
            elif choice == "9":
                identify_vulnerable_hosts()
            elif choice == "10":
                exploit_vulnerable_hosts()
            elif choice == "11":
                clear_all_chunks()
            elif choice == "12":
                split_large_csvs()
            elif choice == "13":
                bruteforce_ssh()
            elif choice == "14":
                print("Exiting...")
                break
            else:
                print("[ERROR] Invalid choice. Please try again.")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    ensure_environment()
    main_menu()
