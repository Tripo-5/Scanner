from globals import *
from modules.proxy_handler import load_proxies, test_proxies, scrape_proxies
from modules.host_handler import load_hosts, test_hosts
from modules.scanner import scan_hosts
from modules.bruteforce import bruteforce_ssh
from modules.stats_handler import display_statistics
from webapp.app import start_webapp

import os
import threading
import keyboard

# Task Manager Functions
def toggle_background_task(task_name, function, *args):
    if task_name in active_tasks and active_tasks[task_name].is_alive():
        print(f"[INFO] {task_name} is already running.")
    else:
        print(f"[INFO] Starting {task_name} in background...")
        thread = threading.Thread(target=function, args=args, daemon=True)
        active_tasks[task_name] = thread
        thread.start()

def main_menu():
    while True:
        print("\033[H\033[J", end="")
        display_statistics()

        print("\n[ Main Menu ]")
        print(f"1.) Load Proxies")
        print(f"2.) Test Proxies")
        print(f"3.) Load Hosts")
        print(f"4.) Test Hosts")
        print(f"5.) Scan Hosts")
        print(f"6.) Start Web Interface")
        print(f"7.) Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            load_proxies()
        elif choice == "2":
            toggle_background_task("proxy_test", test_proxies, proxy_stats)
        elif choice == "3":
            load_hosts()
        elif choice == "4":
            toggle_background_task("host_test", test_hosts, host_stats)
        elif choice == "5":
            toggle_background_task("host_scan", scan_hosts)
        elif choice == "6":
            toggle_background_task("web_server", start_webapp)
        elif choice == "7":
            exit()

if __name__ == "__main__":
    main_menu()
