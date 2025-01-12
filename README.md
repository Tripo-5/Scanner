
SSH Vulnerability Scanner and Exploitation Tool

This project is a comprehensive tool for scanning, testing, and exploiting SSH vulnerabilities. It includes modules for proxy management, host scanning, SSH bruteforcing, and vulnerability exploitation. Designed for advanced penetration testing, the tool provides a menu-driven interface for ease of use.
Features

    Proxy Management: Fetch, test, and manage proxies.
    Host Scanning: Load and test IP ranges or host files for SSH servers.
    Vulnerability Identification: Detect potential vulnerabilities based on SSH banners.
    Bruteforcing: Perform SSH login bruteforcing using customizable wordlists.
    Results Management: View and clear results easily.
    CSV Splitting: Split large CSVs into smaller chunks for efficient processing.

Requirements

Ensure you have Python 3.8+ installed. Install the dependencies listed in the requirements.txt file:
Installation

git clone https://github.com/Tripo-5/Scanner.git

cd Scanner

pip3 install -r requirements.txt


Usage

Run the tool by executing the main.py script:

python3 main.py

Menu Options

    Load Proxies: Load proxy files or use default untested proxies.
    Test Proxies: Validate loaded proxies and save live ones.
    Load Hosts: Load a list of IPv4 hosts for scanning.
    Load IP Ranges: Load and split IP ranges for processing.
    Test Hosts: Validate live hosts from the loaded hosts or ranges.
    Scan Hosts: Scan live hosts for SSH services and fetch banners.
    Show Results: View scan results.
    Clear Results: Clear scan results.
    Identify Vulnerabilities: Identify vulnerable SSH versions based on banners.
    Exploit Vulnerable Hosts: Attempt exploitation of detected vulnerable hosts.
    Clear All Chunks: Remove all generated CSV chunks.
    Split Large CSVs: Split large CSV files into manageable chunks.
    SSH Bruteforce: Bruteforce SSH servers using loaded valid hosts and wordlists.
    Exit: Exit the application.

Directory Structure

.
├── README.md
├── main.py
├── requirements.txt

├── ip_ranges/
│   ├── China/
│   ├── Iran/
│   ├── ...

├── modules/
│   ├── proxy_handler.py
│   ├── host_handler.py
│   ├── scanner.py
│   ├── exploit.py
│   ├── utils.py
│   ├── bruteforce.py

├── proxy_ranges/
│   ├── Tested/
│   ├── Untested/

├── results/
│   ├── valid_hosts.txt
│   ├── vulnerable_hosts.txt

├── wordlists/
│   ├── ssh_usernames.txt
│   ├── ssh_passwords.txt

Wordlists

Place your SSH username and password wordlists in the wordlists/ directory:

    ssh_usernames.txt: Contains usernames (e.g., root, admin).
    ssh_passwords.txt: Contains passwords (e.g., 123456, password).

Dependencies

All dependencies are listed in requirements.txt:
requirements.txt

paramiko==2.11.0
requests==2.28.2
beautifulsoup4==4.12.2
tqdm==4.64.1
pysocks==1.7.1

Notes

    Ensure appropriate permissions for writing files in directories such as proxy_ranges/ and results/.
    This tool is intended for ethical hacking and penetration testing with explicit authorization. Unauthorized use is strictly prohibited.
