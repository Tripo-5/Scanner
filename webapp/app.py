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
@app.route("/proxies/test", methods=["POST"])
def test_proxies_route():
    test_proxies()
    return jsonify({"message": "Proxy testing started!"})

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
