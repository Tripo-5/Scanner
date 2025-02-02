import sys
import os

# Ensure Python can find modules from the root directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from modules.proxy_handler import test_proxies, load_proxies  # Now it should work!
from globals import web_config, active_tasks, proxy_stats, host_stats, brute_stats
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import threading
import os
import sqlite3
from modules.host_handler import test_hosts, load_hosts
from modules.bruteforce import bruteforce_ssh

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this!

# Ensure Database Setup
DATABASE = "webapp/database.db"

def init_db():
    """Initialize the database"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))  # Default Credentials
        conn.commit()

@app.route('/')
def index():
    """Render the main dashboard"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', proxy_stats=proxy_stats, host_stats=host_stats, brute_stats=brute_stats, active_tasks=active_tasks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            if user:
                session['user'] = username
                return redirect(url_for('index'))
            else:
                return "Invalid Credentials!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/start_proxy_test')
def start_proxy_test():
    """Start Proxy Testing"""
    if 'proxy_test' not in active_tasks:
        thread = threading.Thread(target=test_proxies, args=(load_proxies(),), daemon=True)
        active_tasks["proxy_test"] = thread
        thread.start()
        return jsonify({"message": "Proxy testing started!"})
    return jsonify({"message": "Proxy testing already running!"})

@app.route('/start_host_scan')
def start_host_scan():
    """Start Host Scanning"""
    if 'host_scan' not in active_tasks:
        thread = threading.Thread(target=test_hosts, args=(load_hosts(),), daemon=True)
        active_tasks["host_scan"] = thread
        thread.start()
        return jsonify({"message": "Host scanning started!"})
    return jsonify({"message": "Host scanning already running!"})

@app.route('/start_bruteforce')
def start_bruteforce():
    """Start SSH Bruteforce"""
    if 'bruteforce' not in active_tasks:
        thread = threading.Thread(target=bruteforce_ssh, args=(host_stats["total"],), daemon=True)
        active_tasks["bruteforce"] = thread
        thread.start()
        return jsonify({"message": "Bruteforce started!"})
    return jsonify({"message": "Bruteforce already running!"})

# Load Proxies
@app.route('/load_proxies', methods=['POST'])
def load_proxies_route():
    global proxy_stats
    proxy_stats["total"] = len(load_proxies())
    flash("Proxies loaded successfully!", "success")
    return redirect(url_for('dashboard'))

# Scrape Proxies
@app.route('/scrape_proxies', methods=['POST'])
def scrape_proxies_route():
    threading.Thread(target=scrape_proxies, daemon=True).start()
    flash("Started scraping proxies!", "success")
    return redirect(url_for('dashboard'))

# Test Proxies
@app.route('/test_proxies', methods=['POST'])
def test_proxies_route():
    threading.Thread(target=test_proxies, args=(proxy_stats["total"],), daemon=True).start()
    flash("Started testing proxies!", "success")
    return redirect(url_for('dashboard'))

# Clear Proxies
@app.route('/clear_proxies', methods=['POST'])
def clear_proxies_route():
    clear_proxies()
    flash("Cleared all proxies!", "success")
    return redirect(url_for('dashboard'))

# Load Hosts
@app.route('/load_hosts', methods=['POST'])
def load_hosts_route():
    global host_stats
    host_stats["total"] = len(load_hosts())
    flash("Hosts loaded successfully!", "success")
    return redirect(url_for('dashboard'))

# Load IP Ranges
@app.route('/load_ip_ranges', methods=['POST'])
def load_ip_ranges_route():
    global host_stats
    host_stats["total"] = len(load_ip_ranges())
    flash("IP ranges loaded successfully!", "success")
    return redirect(url_for('dashboard'))

# Test Hosts
@app.route('/test_hosts', methods=['POST'])
def test_hosts_route():
    threading.Thread(target=test_hosts, args=(host_stats["total"],), daemon=True).start()
    flash("Started testing hosts!", "success")
    return redirect(url_for('dashboard'))

# Scan Hosts
@app.route('/scan_hosts', methods=['POST'])
def scan_hosts_route():
    threading.Thread(target=scan_hosts, daemon=True).start()
    flash("Started scanning hosts!", "success")
    return redirect(url_for('dashboard'))

# Brute-force Attack (Python)
@app.route('/bruteforce_python', methods=['POST'])
def bruteforce_python_route():
    threading.Thread(target=bruteforce_ssh, daemon=True).start()
    flash("Started Python SSH Bruteforce!", "success")
    return redirect(url_for('dashboard'))

# Tor Proxy Control
@app.route('/start_tor', methods=['POST'])
def start_tor_route():
    start_tor()
    flash("Started Tor Proxy!", "success")
    return redirect(url_for('dashboard'))

@app.route('/renew_tor', methods=['POST'])
def renew_tor_route():
    renew_tor_ip()
    flash("Renewed Tor IP!", "success")
    return redirect(url_for('dashboard'))

@app.route('/stop_tor', methods=['POST'])
def stop_tor_route():
    stop_tor()
    flash("Stopped Tor Proxy!", "success")
    return redirect(url_for('dashboard'))

# Command & Control
@app.route('/start_apache', methods=['POST'])
def start_apache_route():
    start_apache_server()
    flash("Started Apache Server!", "success")
    return redirect(url_for('dashboard'))

@app.route('/start_listener', methods=['POST'])
def start_listener_route():
    start_listener()
    flash("Started Listener!", "success")
    return redirect(url_for('dashboard'))

@app.route('/stop_listeners', methods=['POST'])
def stop_listeners_route():
    stop_listeners()
    flash("Stopped All Listeners!", "success")
    return redirect(url_for('dashboard'))    

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
