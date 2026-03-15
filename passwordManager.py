from Crypto.Cipher import Salsa20
from Crypto.Hash import HMAC, SHA256
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
import argparse

if __name__ == "__main__":
    # parsiranje argumenata
    parser = argparse.ArgumentParser()

    parser.add_argument("action", type=str)
    parser.add_argument("master", type=str)
    parser.add_argument("url", type=str, nargs="?", default=None)
    parser.add_argument("password", type=str, nargs="?", default=None)

    args = parser.parse_args()

    # inicijalizacija
    if args.action == "init":
        salt = get_random_bytes(16)
        N = 2**14
        r = 8
        p = 1
        # derivacija kljuca pomocu scrypt funkcije
        key = scrypt(args.master, salt, 32, N=2**14, r=8, p=1)
        # inicijalizacija sifre pomocu dobivenog kljuca
        cipher = Salsa20.new(key)
        # inicijalizacija dictionary-a i njegovo sifrovanje
        empty = {}
        ciphertext = cipher.encrypt(empty.__str__().encode())

        # generiranje HMAC-a za provjeru integriteta
        h = HMAC.new(key, digestmod=SHA256)
        h.update(ciphertext)

        # spremanje u datoteku
        with open("passwords.txt", "wb") as f:
            f.write(salt)
            f.write(N.to_bytes(4, "big"))
            f.write(r.to_bytes(4, "big"))
            f.write(p.to_bytes(4, "big"))
            f.write(cipher.nonce)
            f.write(h.digest())
            f.write(ciphertext)

        print("Password manager initialized.")

    # Dodavanje nove lozinke
    if args.action == "put":

        # citanje iz datoteke
        with open("passwords.txt", "rb") as f:
            salt = f.read(16)
            N = int.from_bytes(f.read(4), "big")
            r = int.from_bytes(f.read(4), "big")
            p = int.from_bytes(f.read(4), "big")
            nonce = f.read(8)
            mac = f.read(32)
            ciphertext = f.read()

        # deriviranje istog kljuca kao i prilikom inicijalizacije
        key = scrypt(args.master, salt, 32, N=N, r=r, p=p)
        cipher = Salsa20.new(key=key, nonce=nonce)

        # provjera integriteta pomocu HMAC-a
        h = HMAC.new(key, digestmod=SHA256)
        h.update(ciphertext)
        try:
            h.verify(mac)
        except ValueError:
            print("Master password incorrect or integrity check failed.")
            exit(1)

        # dekriptovanje i upisivanje u dictionary
        decrypted = cipher.decrypt(ciphertext)
        dict_data = eval(decrypted.decode())
        dict_data[args.url] = args.password

        # ponovno sifrovanje i izracunavanje novog HMAC-a
        new_cipher = Salsa20.new(key=key)
        new_ciphertext = new_cipher.encrypt(dict_data.__str__().encode())
        new_mac = HMAC.new(key, digestmod=SHA256)
        new_mac.update(new_ciphertext)

        # spremanje u datoteku
        with open("passwords.txt", "wb") as f:
            f.write(salt)
            f.write(N.to_bytes(4, "big"))
            f.write(r.to_bytes(4, "big"))
            f.write(p.to_bytes(4, "big"))
            f.write(new_cipher.nonce)
            f.write(new_mac.digest())
            f.write(new_ciphertext)

    # dohvacanje lozinke
    if args.action == "get":
        #citanje iz datoteke
        with open("passwords.txt", "rb") as f:
            salt = f.read(16)
            N = int.from_bytes(f.read(4), "big")
            r = int.from_bytes(f.read(4), "big")
            p = int.from_bytes(f.read(4), "big")
            nonce = f.read(8)
            mac = f.read(32)
            ciphertext = f.read()

        # deriviranje istog kljuca kao i prilikom inicijalizacije
        key = scrypt(args.master, salt, 32, N=N, r=r, p=p)
        cipher = Salsa20.new(key=key, nonce=nonce)

        # provjera integriteta pomocu HMAC-a
        h = HMAC.new(key, digestmod=SHA256)
        h.update(ciphertext)
        try:
            h.verify(mac)
        except ValueError:
            print("Master password incorrect or integrity check failed.")
            exit(1)

        # dekriptovanje i dohvacanje lozinke
        decrypted = cipher.decrypt(ciphertext)
        dict_data = eval(decrypted.decode())
        if args.url not in dict_data:
            print("No password found for " + args.url)
            exit(1)
        print("Password for " + args.url + " is: " + dict_data.get(args.url))