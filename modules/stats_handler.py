import os
import platform
from termcolor import colored
from globals import active_tasks, proxy_stats, host_stats, brute_stats  # ✅ Ensure correct import

def clear_screen():
    """Clear the terminal screen based on OS."""
    if platform.system() == "Windows":
        os.system("cls")  # ✅ Windows uses 'cls'
    else:
        os.system("clear")  # ✅ Linux/macOS use 'clear'

def display_statistics():
    """Show system stats dynamically with OS compatibility"""
    clear_screen()  # Use OS-specific command to clear terminal

    print("\n[ SYSTEM STATISTICS ]")
    print(colored(f"🟢 Active Background Tasks:  {len(active_tasks)}", "green"))

    print(f"\n📡 Proxies: {colored(proxy_stats.get('total', 0), 'white')} Total | "
          f"{colored(proxy_stats.get('valid', 0), 'green')} Valid | "
          f"{colored(proxy_stats.get('dead', 0), 'red')} Dead | "
          f"{colored(proxy_stats.get('remaining', 0), 'yellow')} Remaining")

    print(f"🌐 Hosts: {colored(host_stats.get('total', 0), 'white')} Total | "
          f"{colored(host_stats.get('valid', 0), 'green')} Live | "
          f"{colored(host_stats.get('dead', 0), 'red')} Dead | "
          f"{colored(host_stats.get('remaining', 0), 'yellow')} Remaining")

    print(f"🔑 Brute-force: {colored(brute_stats.get('running', 0), 'white')} Running | "
          f"{colored(brute_stats.get('success', 0), 'green')} Success | "
          f"{colored(brute_stats.get('failed', 0), 'red')} Failed\n")
