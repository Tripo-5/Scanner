from modules.proxy_handler import load_proxies, test_proxies
from modules.host_handler import load_hosts, load_ip_ranges, test_hosts
from modules.scanner import scan_hosts, show_results, clear_results
from modules.exploit import identify_vulnerable_hosts, exploit_vulnerable_hosts
from modules.utils import clear_all_chunks, split_large_csvs, ensure_wordlists, ensure_valid_hosts
from modules.bruteforce import load_wordlists, bruteforce_ssh
import os

# Main menu function remains unchanged
def main_menu():
    while True:
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
        print("13.) SSH Bruteforce")
        print("14.) Exit")

        choice = input("Enter your choice: ")
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
            base_dir = "ip_ranges"
            max_lines = input("Enter the maximum number of lines per chunk (default 200): ")
            try:
                max_lines = int(max_lines) if max_lines else 200
            except ValueError:
                max_lines = 200
            split_large_csvs(base_dir, max_lines)
        elif choice == "13":
            print("\n[ SSH Bruteforce Selected ]")
            # Load valid hosts
            valid_hosts_file = "results/valid_hosts.txt"
            if not os.path.exists(valid_hosts_file):
                print("[ERROR] No valid SSH servers found in 'results/valid_hosts'.")
                continue

            with open(valid_hosts_file, "r") as f:
                targets = [line.strip() for line in f if line.strip()]

            if not targets:
                print("[ERROR] No valid SSH servers found.")
                continue

            # Load wordlists
            usernames, passwords = load_wordlists()
            if not usernames or not passwords:
                print("[ERROR] Unable to proceed with SSH bruteforce due to missing or empty wordlists.")
                continue

            # Perform bruteforce
            bruteforce_ssh(targets, usernames, passwords, max_threads=5)

        elif choice == "14":
            print("[INFO] Exiting.")
            break
        else:
            print("[ERROR] Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main_menu()

