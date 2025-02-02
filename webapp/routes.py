from flask import render_template, jsonify
from webapp import app
from globals import proxy_stats, host_stats, brute_stats

@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/api/stats")
def api_stats():
    return jsonify({
        "proxies": proxy_stats,
        "hosts": host_stats,
        "bruteforce": brute_stats
    })
