import os
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# AES Encryption Functions
def aes_encrypt(data, key):
    """
    Encrypt data using AES-CBC.

    :param data: Data to encrypt.
    :param key: AES encryption key.
    :return: Encrypted data with IV prepended.
    """
    try:
        cipher = AES.new(key, AES.MODE_CBC)
        iv = cipher.iv
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))
        return iv + encrypted_data
    except Exception as e:
        print(f"[ERROR] AES encryption failed: {e}")
        return None

def aes_decrypt(encrypted_data, key):
    """
    Decrypt AES-CBC encrypted data.

    :param encrypted_data: Encrypted data with IV prepended.
    :param key: AES decryption key.
    :return: Decrypted data.
    """
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
    """
    Encode data in Base64 format.

    :param data: Data to encode.
    :return: Base64 encoded data.
    """
    try:
        encoded = base64.b64encode(data)
        print("[INFO] Data successfully encoded in Base64.")
        return encoded
    except Exception as e:
        print(f"[ERROR] Base64 encoding failed: {e}")
        return None

def base64_decode(encoded_data):
    """
    Decode data from Base64 format.

    :param encoded_data: Base64 encoded data.
    :return: Decoded data.
    """
    try:
        decoded = base64.b64decode(encoded_data)
        print("[INFO] Data successfully decoded from Base64.")
        return decoded
    except Exception as e:
        print(f"[ERROR] Base64 decoding failed: {e}")
        return None

# Key Generation
def generate_aes_key():
    """
    Generate a random AES encryption key (16 bytes for AES-128).

    :return: Generated AES key.
    """
    key = os.urandom(16)
    print(f"[INFO] AES key generated: {base64.b64encode(key).decode()}")
    return key
