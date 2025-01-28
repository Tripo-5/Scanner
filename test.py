from modules.proxy_handler import scrape_proxies, test_proxies
from modules.host_handler import load_hosts, test_hosts
from modules.bruteforce import load_wordlists, bruteforce_ssh
from modules.scanner import scan_hosts
import os

# Step 1: Proxy Scanning and Testing
def scan_and_test_proxies():
    print("[INFO] Scanning and testing proxies...")
    scrape_proxies()  # Scrapes proxies and saves them to global_scraped_proxies
    test_proxies()    # Tests scraped proxies and updates global_tested_proxies

# Step 2: Load and Test Hosts
def load_and_test_hosts():
    print("[INFO] Loading and testing hosts...")
    load_hosts()       # Loads hosts into global_hosts
    test_hosts()       # Tests each host to find live hosts and updates global_live_hosts

# Step 3: Brute-Force Live Hosts
def brute_force_live_hosts():
    print("[INFO] Starting brute force attacks on live hosts...")
    usernames, passwords = load_wordlists()  # Loads usernames and passwords from wordlists
    bruteforce_ssh(usernames, passwords)     # Performs SSH brute force on live hosts

# Step 4: Scan Live Hosts for Additional Information
def scan_live_hosts():
    print("[INFO] Scanning live hosts for additional information...")
    scan_hosts()  # Scans live hosts for vulnerabilities or banners

# Main Automation Workflow
def main():
    print("[INFO] Starting the automation workflow...")

    # Step 1: Proxy Scanning and Testing
    scan_and_test_proxies()

    # Step 2: Load and Test Hosts
    load_and_test_hosts()

    # Step 3: Brute-Force Live Hosts
    brute_force_live_hosts()

    # Step 4: Scan Live Hosts
    scan_live_hosts()

    print("[INFO] Automation workflow completed.")

if __name__ == "__main__":
    main()
