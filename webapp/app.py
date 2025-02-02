import os
import threading
import time
import bcrypt
import flask
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from webapp.database import db
from globals import global_scraped_proxies, global_tested_proxies, global_hosts, active_tasks, proxy_stats, host_stats, brute_stats, web_config
from modules.proxy_handler import load_proxies, test_proxies, scrape_proxies, add_proxy_sources, load_checked_proxies, clear_proxies
from modules.host_handler import load_hosts, load_ip_ranges, test_hosts, load_previous_hosts
from modules.scanner import scan_hosts, show_results, clear_results
from modules.exploit import identify_vulnerable_hosts, exploit_vulnerable_hosts
from modules.bruteforce import load_wordlists, bruteforce_ssh
from modules.go_bruteforce import run_golang_bruteforce
from modules.command_control import start_listener, c2_interface, start_apache_server, stop_listeners
from modules.tor_handler import start_tor, renew_tor_ip, stop_tor

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MySQL Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://scanner_user:your_password@localhost/scanner_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# User Authentication Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_login = db.Column(db.Boolean, default=True)

# Ensure database tables exist
with app.app_context():
    db.create_all()

# ==================== AUTHENTICATION ==================== #
@app.route("/", methods=["GET", "POST"])
def login():
    """ User Login Page """
    if "user" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user"] = username
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/logout")
def logout():
    """ User Logout """
    session.pop("user", None)
    return redirect("/")

# ==================== DASHBOARD ==================== #
@app.route("/dashboard")
def dashboard():
    """ Dashboard with Statistics """
    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html", 
        proxy_stats=proxy_stats, 
        host_stats=host_stats, 
        brute_stats=brute_stats, 
        active_tasks=len(active_tasks)
    )

# ==================== PROXY MANAGEMENT ==================== #
@app.route("/proxies/load", methods=["POST"])
def load_proxies_route():
    """ Load Proxies into Global Memory """
    global_scraped_proxies[:] = load_proxies()
    return redirect("/dashboard")

@app.route("/proxies/test", methods=["POST"])
def test_proxies_route():
    """ Start Proxy Testing """
    threading.Thread(target=test_proxies, args=(global_scraped_proxies,), daemon=True).start()
    return redirect("/dashboard")

@app.route("/proxies/scrape", methods=["POST"])
def scrape_proxies_route():
    """ Scrape New Proxies """
    scrape_proxies()
    return redirect("/dashboard")

@app.route("/proxies/clear", methods=["POST"])
def clear_proxies_route():
    """ Clear All Proxies """
    clear_proxies()
    return redirect("/dashboard")

# ==================== HOST MANAGEMENT ==================== #
@app.route("/hosts/load", methods=["POST"])
def load_hosts_route():
    """ Load Hosts """
    global_hosts[:] = load_hosts()
    return redirect("/dashboard")

@app.route("/hosts/test", methods=["POST"])
def test_hosts_route():
    """ Start Testing Hosts """
    threading.Thread(target=test_hosts, args=(global_hosts, global_tested_proxies), daemon=True).start()
    return redirect("/dashboard")

@app.route("/hosts/scan", methods=["POST"])
def scan_hosts_route():
    """ Start Scanning Hosts """
    threading.Thread(target=scan_hosts, daemon=True).start()
    return redirect("/dashboard")

@app.route("/hosts/clear", methods=["POST"])
def clear_hosts_route():
    """ Clear Hosts """
    global_hosts.clear()
    return redirect("/dashboard")

# ==================== BRUTEFORCE MANAGEMENT ==================== #
@app.route("/bruteforce/python", methods=["POST"])
def python_bruteforce_route():
    """ Start Python SSH Bruteforce """
    threading.Thread(target=bruteforce_ssh, args=(global_live_hosts,), daemon=True).start()
    return redirect("/dashboard")

@app.route("/bruteforce/golang", methods=["POST"])
def golang_bruteforce_route():
    """ Start Golang SSH Bruteforce """
    threading.Thread(target=run_golang_bruteforce, args=(global_live_hosts,), daemon=True).start()
    return redirect("/dashboard")

# ==================== TOR MANAGEMENT ==================== #
@app.route("/tor/start", methods=["POST"])
def start_tor_route():
    """ Start Tor Proxy """
    start_tor()
    return redirect("/dashboard")

@app.route("/tor/renew", methods=["POST"])
def renew_tor_route():
    """ Renew Tor IP """
    renew_tor_ip()
    return redirect("/dashboard")

@app.route("/tor/stop", methods=["POST"])
def stop_tor_route():
    """ Stop Tor """
    stop_tor()
    return redirect("/dashboard")

# ==================== WEB SERVER CONTROL ==================== #
@app.route("/web/toggle", methods=["POST"])
def toggle_webserver_route():
    """ Start/Stop Web Server """
    if web_config["enabled"]:
        os.system("pkill -f app.py")
        web_config["enabled"] = False
    else:
        threading.Thread(target=lambda: os.system("python3 webapp/app.py &"), daemon=True).start()
        web_config["enabled"] = True
    return redirect("/dashboard")

# ==================== SYSTEM STATUS API ==================== #
@app.route("/status")
def status():
    """ Return System Stats as JSON """
    return jsonify({
        "active_tasks": len(active_tasks),
        "proxy_stats": proxy_stats,
        "host_stats": host_stats,
        "brute_stats": brute_stats
    })

# ==================== MAIN EXECUTION ==================== #
if __name__ == "__main__":
    app.run(host=web_config["host"], port=web_config["port"], debug=True)
