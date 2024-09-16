import hashlib
from tqdm import tqdm
import argparse

# Supported hash types
hash_types = {'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512'}

def crack_password(hash_value, wordlist, hash_type='md5'):
    if hash_type not in hash_types:
        raise ValueError(f"[+] Invalid hash type: {hash_type}, check supported types: {hash_types}")

    total_words = sum(1 for _ in open(wordlist, 'r', encoding='latin-1'))
    print(f"[+] Cracking hash {hash_value} using {hash_type} with a list of {total_words} words.")

    with open(wordlist, 'r', encoding='latin-1') as f:
        for word in tqdm(f, desc='Cracking hash', total=total_words):
            hashed_word = hashlib.new(hash_type, word.strip().encode()).hexdigest()
            if hashed_word == hash_value:
                return word.strip()

    return "Password not found in the given wordlist."

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crack a hash using a wordlist.')
    parser.add_argument('hash', help='The hash to crack')
    parser.add_argument('wordlist', help='The path to the wordlist')
    parser.add_argument('--hash_type', help='The hash type to use (default: md5)', default='md5')
    args = parser.parse_args()

    try:
        result = crack_password(args.hash, args.wordlist, args.hash_type)
        print("[+] Found password =>", result)
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"[!] An error occurred: {e}")
