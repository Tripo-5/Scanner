import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt
from globals import global_hosts, global_live_hosts, global_tested_proxies
from modules.proxy_handler import load_proxies, test_proxies
from modules.host_handler import load_hosts, load_ip_ranges, test_hosts
from modules.scanner import scan_hosts, show_results, clear_results
from modules.exploit import identify_vulnerable_hosts, exploit_vulnerable_hosts
from modules.utils import clear_all_chunks, split_large_csvs
from modules.bruteforce import load_wordlists, bruteforce_ssh

class SSHScannerGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window settings
        self.setWindowTitle("SSH Vulnerability Scanner")
        self.setGeometry(100, 100, 800, 600)

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Status label
        self.status_label = QLabel("Ready", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Log output area
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        # Buttons
        self.load_proxies_btn = QPushButton("Load Proxies", self)
        self.load_proxies_btn.clicked.connect(self.load_proxies)
        layout.addWidget(self.load_proxies_btn)

        self.test_proxies_btn = QPushButton("Test Proxies", self)
        self.test_proxies_btn.clicked.connect(self.test_proxies)
        layout.addWidget(self.test_proxies_btn)

        self.load_hosts_btn = QPushButton("Load Hosts", self)
        self.load_hosts_btn.clicked.connect(self.load_hosts)
        layout.addWidget(self.load_hosts_btn)

        self.test_hosts_btn = QPushButton("Test Hosts", self)
        self.test_hosts_btn.clicked.connect(self.test_hosts)
        layout.addWidget(self.test_hosts_btn)

        self.scan_hosts_btn = QPushButton("Scan Hosts", self)
        self.scan_hosts_btn.clicked.connect(self.scan_hosts)
        layout.addWidget(self.scan_hosts_btn)

        self.show_results_btn = QPushButton("Show Results", self)
        self.show_results_btn.clicked.connect(self.show_results)
        layout.addWidget(self.show_results_btn)

        self.clear_results_btn = QPushButton("Clear Results", self)
        self.clear_results_btn.clicked.connect(self.clear_results)
        layout.addWidget(self.clear_results_btn)

        self.identify_vulns_btn = QPushButton("Identify Vulnerabilities", self)
        self.identify_vulns_btn.clicked.connect(self.identify_vulnerabilities)
        layout.addWidget(self.identify_vulns_btn)

        self.exploit_vulns_btn = QPushButton("Exploit Vulnerabilities", self)
        self.exploit_vulns_btn.clicked.connect(self.exploit_vulnerabilities)
        layout.addWidget(self.exploit_vulns_btn)

        self.bruteforce_btn = QPushButton("SSH Bruteforce", self)
        self.bruteforce_btn.clicked.connect(self.ssh_bruteforce)
        layout.addWidget(self.bruteforce_btn)

    def log(self, message):
        """Update log output."""
        self.log_output.append(message)
        self.log_output.ensureCursorVisible()

    def load_proxies(self):
        self.log("[INFO] Loading proxies...")
        global global_hosts
        global_hosts[:] = load_proxies()
        self.log(f"[INFO] Loaded {len(global_hosts)} proxies.")

    def test_proxies(self):
        self.log("[INFO] Testing proxies...")
        global global_tested_proxies
        global_tested_proxies[:] = test_proxies(global_hosts)
        self.log(f"[INFO] {len(global_tested_proxies)} working proxies found.")

    def load_hosts(self):
        self.log("[INFO] Loading hosts...")
        global global_hosts
        global_hosts[:] = load_hosts()
        self.log(f"[INFO] Loaded {len(global_hosts)} hosts.")

    def test_hosts(self):
        self.log("[INFO] Testing hosts...")
        global global_live_hosts
        global_live_hosts[:] = test_hosts(global_hosts, global_tested_proxies)
        self.log(f"[INFO] {len(global_live_hosts)} live hosts found.")

    def scan_hosts(self):
        self.log("[INFO] Scanning hosts...")
        scan_hosts()
        self.log("[INFO] Scan complete.")

    def show_results(self):
        self.log("[INFO] Showing scan results...")
        show_results()

    def clear_results(self):
        self.log("[INFO] Clearing results...")
        clear_results()
        self.log("[INFO] Results cleared.")

    def identify_vulnerabilities(self):
        self.log("[INFO] Identifying vulnerabilities...")
        global global_vulnerable_hosts
        global_vulnerable_hosts[:] = identify_vulnerable_hosts(global_live_hosts)
        self.log(f"[INFO] Found {len(global_vulnerable_hosts)} vulnerable hosts.")

    def exploit_vulnerabilities(self):
        self.log("[INFO] Exploiting vulnerable hosts...")
        exploit_vulnerable_hosts(global_vulnerable_hosts)
        self.log("[INFO] Exploitation complete.")

    def ssh_bruteforce(self):
        self.log("[INFO] Starting SSH Bruteforce...")
        if not global_live_hosts:
            self.log("[ERROR] No live hosts available.")
            return

        targets = global_live_hosts
        usernames, passwords = load_wordlists()
        if not usernames or not passwords:
            self.log("[ERROR] Missing or empty wordlists.")
            return

        thread = threading.Thread(
            target=bruteforce_ssh, args=(targets, usernames, passwords, 5)
        )
        thread.start()
        self.log("[INFO] Bruteforce in progress...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SSHScannerGUI()
    window.show()
    sys.exit(app.exec())
