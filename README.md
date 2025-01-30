# This tool is intended for ethical hacking and penetration testing with explicit authorization. Unauthorized use is strictly prohibited. Strictly for Educational Use.

# SSH Vulnerability Scanner and Exploitation Tool (GUI & CLI)
# A comprehensive tool for scanning, testing, and exploiting SSH vulnerabilities. It supports proxy management, SSH bruteforcing, vulnerability scanning, and reverse shell payloads. The tool includes both a Command-Line Interface (CLI) and a Graphical User Interface
# (GUI).

Installation
Ensure you have Python 3.8+ installed. Then, install the required dependencies:

`git clone https://github.com/Tripo-5/Scanner.git
cd Scanner
pip3 install -r requirements.txt`

## Usage
###🔹 CLI Mode Run the tool via CLI using:

`python3 main.py`

###🔹 GUI Mode (New) To run the Graphical User Interface (GUI) version:

`sh
python3 gui.py`

###🔹 Ensure you have installed PyQt6 using:

`pip install PyQt6`


🛠️ Features
✅ Proxy Management: Scrape, load, test, and manage SOCKS5 proxies.
✅ IP Range & Host Management: Load IP ranges, split large datasets, and test hosts.
✅ SSH Vulnerability Scanning: Detect potential vulnerabilities based on SSH banners.
✅ SSH Bruteforcing: Perform brute-force attacks using customizable wordlists.
✅ Reverse Shell Generation: Generate encrypted reverse shell payloads for Windows, Linux, and macOS.
✅ Cryptominer Management: Encrypt and manage cryptominer binaries.
✅ Command & Control (C2) Center: Manage listener sessions and remote connections.
✅ Configurable Settings: Save tool settings and configurations for later use.
✅ Pause/Resume & Stop Scans: Use F5 to pause and F6 to stop scans at any time.

### 📜 Menu Options
>🔹 1.) Add Proxy Sources – Add new proxy sources for scraping.
>🔹 2.) Scrape Proxies – Scrape and extract proxies from the provided sources.
>🔹 3.) Load Proxies – Load proxy files for testing and scanning.
>🔹 4.) Test Proxies – Validate and save working proxies.
>🔹 5.) Load Hosts – Load a list of IPv4 hosts for scanning.
>🔹 6.) Load IP Ranges – Load and split IP ranges for processing.
>🔹 7.) Test Hosts – Validate live hosts using SOCKS5 proxies.
>🔹 8.) Scan Hosts – Scan live hosts for SSH services and fetch banners.
>🔹 9.) Show Results – View scan results.
>🔹 10.) Clear Results – Clear scan results.
>🔹 11.) Identify Vulnerabilities – Identify vulnerable SSH versions based on banners.
>🔹 12.) Exploit Vulnerable Hosts – Attempt exploitation of detected vulnerable hosts.
>🔹 13.) Clear All Chunks – Remove all generated CSV chunks.
>🔹 14.) Split Large CSVs – Split large CSV files into manageable chunks.
>🔹 15.) SSH Bruteforce – Bruteforce SSH servers using loaded valid hosts and wordlists.
>🔹 16.) Configuration Settings – Manage tool configurations and settings.
>🔹 17.) Generate Reverse Shell – Generate and encrypt reverse shells for different platforms.
>🔹 18.) Manage Cryptominers – Encrypt and manage cryptominer binaries.
>🔹 19.) Command & Control Center – Manage active sessions and listener options.
>🔹 20.) Exit – Exit the application.

### 📂 Directory Structure
> .
> ├── README.md
> ├── main.py
> ├── gui.py
> ├── requirements.txt
> ├── ip_ranges/
> │   ├── China/
> │   ├── Iran/
> │   ├── ...
> ├── modules/
> │   ├── proxy_handler.py
> │   ├── host_handler.py
> │   ├── scanner.py
> │   ├── exploit.py
> │   ├── utils.py
> │   ├── bruteforce.py
> │   ├── shell_generator.py
> │   ├── miner_payload.py
> │   ├── command_control.py
> │   ├── config_handler.py
> ├── payloads/
> │   ├── cryptominers/
> ├── proxy_lists/
> │   ├── unchecked_proxies.txt
> │   ├── checked_proxies.txt
> │   ├── proxy_sources.txt
> ├── results/
> │   ├── valid_hosts.txt
> │   ├── vulnerable_hosts.txt
> ├── wordlists/
> │   ├── ssh_usernames.txt
> │   ├── ssh_passwords.txt
### 📜 Wordlists Place your SSH username and password wordlists inside the wordlists/ directory:

> ssh_usernames.txt – Common usernames (e.g., root, admin).
> ssh_passwords.txt – Common passwords (e.g., 123456, password).

### 🛠️ Dependencies The required dependencies are listed in requirements.txt:
> paramiko==2.11.0
> requests==2.28.2
> beautifulsoup4==4.12.2
> tqdm==4.64.1
> pysocks==1.7.1
> cryptography==39.0.1
> pycryptodome==3.16.0
> mysql-connector-python
> PyQt6==6.5.0  # Required for GUI mode
> keyboard==0.13.5  # Required for F5 & F6 bindings


###To install dependencies:

`pip install -r requirements.txt`

### ⚙️ Key Features
> ✅ Graphical User Interface (GUI) – Run the tool in GUI mode using python3 gui.py.
> ✅ Pause (F5) / Stop (F6) Key Bindings – Control scanning in real-time.
> ✅ Fully Integrated C2 (Command & Control) Center – Manage reverse shells remotely.
> ✅ Encrypted Reverse Shells – Generate payloads that mimic legitimate files.
> ✅ Multithreaded Scanning – Fast and efficient scanning without GUI freezing.
> ✅ Integrated Cryptominer Management – Secure and encrypt cryptominer binaries.
> ✅ Supports SOCKS5 Proxies – Scan using anonymized connections.

### 🚨 Notes
### ⚠️ This tool is intended for ethical hacking and penetration testing with explicit authorization.
### ⚠️ Unauthorized use is strictly prohibited.
### ⚠️ Ensure appropriate permissions for writing files in directories such as proxy_lists/ and results/.

### 🛠️ Future Enhancements
> 🔹 Add more encryption methods for payloads (AES, XOR, obfuscation).
> 🔹 GUI Enhancements (real-time logs, session tracking).
> 🔹 Advanced C2 Server integration.
> 🔹 Better SOCKS5 Proxy Integration for stealth scanning.
