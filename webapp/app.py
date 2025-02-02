from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import threading
import os
import sqlite3
from globals import web_config, active_tasks, proxy_stats, host_stats, brute_stats
from modules.proxy_handler import test_proxies, load_proxies
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

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
