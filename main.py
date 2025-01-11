from modules.proxy_handler import load_proxies, test_proxies
from modules.host_handler import load_hosts, load_ip_ranges, test_hosts
from modules.scanner import scan_hosts, show_results, clear_results
from modules.exploit import bruteforce, identify_vulnerable_hosts, exploit_vulnerable_hosts
from modules.utils import clear_all_chunks
# Main menu function remains unchanged
def main_menu():
    while True:
        print("\n[ Main Menu ]")
        print("1.) Load Proxies")
        print("2.) Test Proxies")
        print("3.) Load Hosts")
        print("4.) Load IP Ranges")
        print("5.) Test Hosts")
        print("6.) Scan Hosts")
        print("7.) Show Results")
        print("8.) Clear Results")
        print("9.) Bruteforce")
        print("10.) Show Valid")
        print("11.) Check Vulnerabilities")
        print("12.) Exploit Vulnerable Hosts")
        print("13.) Clear Chunks from countries")
        print("14.) Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            load_proxies()
        elif choice == "2":
            test_proxies()
        elif choice == "3":
            load_hosts()
        elif choice == "4":
            load_ip_ranges()
        elif choice == "5":
            test_hosts()
        elif choice == "6":
            scan_hosts()
        elif choice == "7":
            show_results()
        elif choice == "8":
            clear_results()
        elif choice == "9":
            bruteforce()
        elif choice == "10":
            show_valid()
        elif choice == "11":
            identify_vulnerable_hosts()
        elif choice == "12":
            exploit_vulnerable_hosts()
        elif choice == "13":
            clear_all_chunks()
        elif choice == "14":
            print("[INFO] Exiting.")
            break
        else:
            print("[ERROR] Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main_menu()

