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
    """Scrape proxies from sources."""
    scrape_proxies()
    return jsonify({"message": "Proxies scraped successfully!"}), 200

@app.route("/proxies/load", methods=["POST"])
def load_proxies_route():
    """Load scraped proxies."""
    global_scraped_proxies = load_proxies()
    if not global_scraped_proxies:
        return jsonify({"error": "No proxies found!"}), 400
    return jsonify({"message": "Proxies loaded!", "count": len(global_scraped_proxies)}), 200

@app.route("/proxies/test", methods=["POST"])
def test_proxies_route():
    """Test loaded proxies."""
    global_scraped_proxies = load_proxies()
    if not global_scraped_proxies:
        return jsonify({"error": "No proxies loaded. Load proxies first!"}), 400
    test_proxies(global_scraped_proxies)
    return jsonify({"message": "Proxy testing started!"}), 200

@app.route("/proxies/save", methods=["POST"])
def save_proxies_route():
    """Save valid proxies to file."""
    save_working_proxies()
    return jsonify({"message": "Valid proxies saved!"}), 200

@app.route("/proxies/load-checked", methods=["POST"])
def load_checked_proxies_route():
    """Load previously tested proxies."""
    global_checked_proxies = load_checked_proxies()
    if not global_checked_proxies:
        return jsonify({"error": "No previously checked proxies found!"}), 400
    return jsonify({"message": "Checked proxies loaded!", "count": len(global_checked_proxies)}), 200


@app.route("/hosts/scan", methods=["POST"])
def scan_hosts_route():
    test_hosts()
    return jsonify({"message": "Host scanning started!"})

@app.route("/bruteforce/start", methods=["POST"])
def start_bruteforce_route():
    bruteforce_ssh()
    return jsonify({"message": "Brute-force started!"})    

if __name__ == "__main__":
    start_webapp()
