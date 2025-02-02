import os
from termcolor import colored
import platform

# Global Stats Dictionary
proxy_stats = {"total": 0, "valid": 0, "dead": 0, "remaining": 0}
host_stats = {"total": 0, "valid": 0, "dead": 0, "remaining": 0}
brute_stats = {"running": 0, "success": 0, "failed": 0}


def clear_screen():
    """Clear the terminal screen based on the OS."""
    if platform.system() == "Windows":
        os.system("cls")  # Windows uses 'cls' to clear the screen
    else:
        os.system("clear")  # Linux/macOS use 'clear'

def display_statistics():
    """Show system stats dynamically with OS compatibility"""
    clear_screen()  # Use the appropriate clear command

    print("\n[ SYSTEM STATISTICS ]")
    print(colored(f"🟢 Active Background Tasks:  {len(active_tasks)}", "green"))

    print(f"\n📡 Proxies: {colored(proxy_stats['total'], 'white')} Total | "
          f"{colored(proxy_stats['valid'], 'green')} Valid | "
          f"{colored(proxy_stats['dead'], 'red')} Dead | "
          f"{colored(proxy_stats['remaining'], 'yellow')} Remaining")

    print(f"🌐 Hosts: {colored(host_stats['total'], 'white')} Total | "
          f"{colored(host_stats['valid'], 'green')} Live | "
          f"{colored(host_stats['dead'], 'red')} Dead | "
          f"{colored(host_stats['remaining'], 'yellow')} Remaining")

    print(f"🔑 Brute-force: {colored(brute_stats['running'], 'white')} Running | "
          f"{colored(brute_stats['success'], 'green')} Success | "
          f"{colored(brute_stats['failed'], 'red')} Failed\n")
