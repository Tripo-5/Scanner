from globals import (
    global_hosts,
    global_live_hosts,
    global_vulnerable_hosts,
    global_scraped_proxies,
    global_tested_proxies,
)
from modules.proxy_handler import load_proxies, test_proxies
from modules.host_handler import load_hosts, load_ip_ranges, test_hosts
from modules.scanner import scan_hosts, show_results, clear_results
from modules.exploit import identify_vulnerable_hosts, exploit_vulnerable_hosts
from modules.utils import clear_all_chunks, split_large_csvs, ensure_wordlists, ensure_valid_hosts
from modules.bruteforce import load_wordlists, bruteforce_ssh
import os

def main_menu():
    global global_hosts, global_live_hosts, global_vulnerable_hosts
    global global_scraped_proxies, global_tested_proxies

    while True:
        print("\n[ Main Menu ]")
        print("1.) Add Proxy Sources")
        print("2.) Scrape Proxies")
        print("3.) Load Proxies")
        print("4.) Test Proxies")
        print("5.) Load Hosts")
        print("6.) Load IP Ranges")
        print("7.) Test Hosts")
        print("8.) Scan Hosts")
        print("9.) Show Results")
        print("10.) Clear Results")
        print("11.) Identify Vulnerabilities")
        print("12.) Exploit Vulnerable Hosts")
        print("13.) Clear All Chunks")
        print("14.) Split Large CSVs")
        print("15.) SSH Bruteforce")
        print("16.) Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            add_proxy_sources()
        elif choice == "2":
            scrape_proxies()
        elif choice == "3":
            global_scraped_proxies = load_proxies()
        elif choice == "4":
            global_tested_proxies = test_proxies(global_scraped_proxies)
        elif choice == "5":
            global_hosts = load_hosts()
        elif choice == "6":
            global_hosts = load_ip_ranges()
        elif choice == "7":
            global_live_hosts = test_hosts(global_hosts, global_tested_proxies)
        elif choice == "8":
            scan_hosts()
        elif choice == "9":
            show_results()
        elif choice == "10":
            clear_results()
        elif choice == "11":
            global_vulnerable_hosts = identify_vulnerable_hosts(global_live_hosts)
        elif choice == "12":
            exploit_vulnerable_hosts(global_vulnerable_hosts)
        elif choice == "13":
            clear_all_chunks()
        elif choice == "14":
            base_dir = "ip_ranges"
            max_lines = input("Enter the maximum number of lines per chunk (default 200): ")
            try:
                max_lines = int(max_lines) if max_lines else 200
            except ValueError:
                max_lines = 200
            split_large_csvs(base_dir, max_lines)
        elif choice == "15":
            print("\n[ SSH Bruteforce Selected ]")
            if not global_live_hosts:
                print("[ERROR] No valid live hosts found in memory.")
                continue
            targets = global_live_hosts
            usernames, passwords = load_wordlists()
            if not usernames or not passwords:
                print("[ERROR] Unable to proceed with SSH bruteforce due to missing or empty wordlists.")
                continue
            bruteforce_ssh(targets, usernames, passwords, max_threads=5)
        elif choice == "16":
            print("[INFO] Exiting.")
            break
        else:
            print("[ERROR] Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main_menu()
