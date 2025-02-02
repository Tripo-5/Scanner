import os
from termcolor import colored

# Global Stats Dictionary
proxy_stats = {"total": 0, "valid": 0, "dead": 0, "remaining": 0}
host_stats = {"total": 0, "valid": 0, "dead": 0, "remaining": 0}
brute_stats = {"running": 0, "success": 0, "failed": 0}

def display_statistics():
    """Show system stats dynamically with color enhancements."""
    os.system("clear")  # Clear screen
    print("\n" + colored("[ SYSTEM STATISTICS ]", "cyan", attrs=["bold"]))

    print(f"🟢 Active Background Tasks: {colored(len(proxy_stats), 'green')}\n")

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
