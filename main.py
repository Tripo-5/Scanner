from modules.proxy_handler import load_proxies, test_proxies
from modules.host_handler import load_hosts, load_ip_ranges, test_hosts
from modules.scanner import scan_hosts, show_results, clear_results
from modules.exploit import identify_vulnerable_hosts, exploit_vulnerable_hosts
from modules.utils import clear_all_chunks, split_large_csvs, ensure_wordlists, ensure_valid_hosts
from modules.bruteforce import load_wordlists, bruteforce_ssh
import os

# Global Variables
global_hosts = []  # Stores all loaded hosts
global_host_selection = []  # Stores selected hosts for operations
global_live_hosts = []  # Stores live hosts detected during testing
global_vulnerable_hosts = []  # Stores hosts identified as vulnerable
global_scraped_proxies = []  # Stores proxies before testing
global_tested_proxies = []  # Stores proxies after testing

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
        print("14.) Enable Tor")
        print("15.) Disable Tor")
        print("16.) Renew Tor IP")
        print("17.) VPN Settings")
        print("18.) Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            global global_scraped_proxies
            global_scraped_proxies = load_proxies()
        elif choice == "2":
            global global_tested_proxies
            global_tested_proxies = test_proxies(global_scraped_proxies)
        elif choice == "3":
            global global_hosts
            global_hosts = load_hosts()
        elif choice == "4":
            global global_hosts
            global_hosts = load_ip_ranges()
        elif choice == "5":
            global global_live_hosts
            global_live_hosts = test_hosts(global_hosts, global_tested_proxies)
        elif choice == "6":
            scan_hosts(global_live_hosts, global_tested_proxies)
        elif choice == "7":
            show_results()
        elif choice == "8":
            clear_results()
        elif choice == "9":
            global global_vulnerable_hosts
            global_vulnerable_hosts = identify_vulnerable_hosts(global_live_hosts)
        elif choice == "10":
            exploit_vulnerable_hosts(global_vulnerable_hosts)
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
        elif choice == "13":  # SSH Bruteforce option
            print("\n[ SSH Bruteforce Selected ]")
            if not global_live_hosts:  # Check if live hosts are available
                print("[ERROR] No valid live hosts found in memory.")
                continue
        
            targets = global_live_hosts  # Pass live hosts as targets
        
            # Load wordlists
            usernames, passwords = load_wordlists()
            if not usernames or not passwords:
                print("[ERROR] Unable to proceed with SSH bruteforce due to missing or empty wordlists.")
                continue
        
            # Perform bruteforce
            bruteforce_ssh(targets, usernames, passwords, max_threads=2)
        elif choice == "14":
            enable_tor()
        elif choice == "15":
            disable_tor()
        elif choice == "16":
            renew_tor_ip()
        elif choice == "17":
            vpn_settings()
        elif choice == "18":
            print("[INFO] Exiting.")
            break
        else:
            print("[ERROR] Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main_menu()
