from webapp import app

def start_webapp():
    """Start the Flask Web Server."""
    app.run(host=web_config["host"], port=web_config["port"], debug=True)

if __name__ == "__main__":
    start_webapp()
