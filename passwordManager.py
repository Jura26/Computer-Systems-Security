from Crypto.Cipher import Salsa20
from Crypto.Hash import HMAC, SHA256

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("action", type=str)
    parser.add_argument("master", type=str)
    parser.add_argument("--url", type=str, required=False)
    parser.add_argument("--password", type=str, required=False)

    args = parser.parse_args()

    if args.action == "init":
        with open("passwords.txt", "wb") as f:
            f.write("".encode("utf-8"))
            h = HMAC.new(args.master.encode("utf-8"), digestmod=SHA256)
            print(h.hexdigest())

