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
        # derivacija kljuca pomocu scrypt funkcije (64 bytes za encryption i mac)
        key = scrypt(args.master, salt, 64, N=2**14, r=8, p=1)
        encKey = key[:32]
        macKey = key[32:]
        # inicijalizacija sifre pomocu dobivenog kljuca
        cipher = Salsa20.new(encKey)
        # inicijalizacija dictionary-a i njegovo sifrovanje
        empty = {}
        ciphertext = cipher.encrypt(empty.__str__().encode())

        # generiranje HMAC-a za provjeru integriteta
        h = HMAC.new(macKey, digestmod=SHA256)
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
        key = scrypt(args.master, salt, 64, N=N, r=r, p=p)
        encKey = key[:32]
        macKey = key[32:]
        cipher = Salsa20.new(key=encKey, nonce=nonce)

        # provjera integriteta pomocu HMAC-a
        h = HMAC.new(macKey, digestmod=SHA256)
        h.update(ciphertext)
        try:
            h.verify(mac)
        except ValueError:
            print("Master password incorrect or integrity check failed.")
            exit(1)

        # dekriptovanje i upisivanje u dictionary nakon dodavanja paddinga
        args.password = args.password.ljust(32, " ")
        args.url = args.url.ljust(32, " ")
        decrypted = cipher.decrypt(ciphertext)
        dictData = eval(decrypted.decode())
        dictData[args.url] = args.password

        # generiranje novog salta i kljuca
        newSalt = get_random_bytes(16)
        newKey = scrypt(args.master, newSalt, 64, N=N, r=r, p=p)
        newEncKey = newKey[:32]
        newMacKey = newKey[32:]

        # ponovno sifrovanje i izracunavanje novog HMAC-a
        newCipher = Salsa20.new(key=newEncKey)
        new_ciphertext = newCipher.encrypt(dictData.__str__().encode())
        new_mac = HMAC.new(newMacKey, digestmod=SHA256)
        new_mac.update(new_ciphertext)

        # spremanje u datoteku
        with open("passwords.txt", "wb") as f:
            f.write(newSalt)
            f.write(N.to_bytes(4, "big"))
            f.write(r.to_bytes(4, "big"))
            f.write(p.to_bytes(4, "big"))
            f.write(newCipher.nonce)
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
        key = scrypt(args.master, salt, 64, N=N, r=r, p=p)
        encKey = key[:32]
        macKey = key[32:]
        cipher = Salsa20.new(key=encKey, nonce=nonce)

        # provjera integriteta pomocu HMAC-a
        h = HMAC.new(macKey, digestmod=SHA256)
        h.update(ciphertext)
        try:
            h.verify(mac)
        except ValueError:
            print("Master password incorrect or integrity check failed.")
            exit(1)

        # dekriptovanje i dohvacanje lozinke
        decrypted = cipher.decrypt(ciphertext)
        dictData = eval(decrypted.decode())
        if args.url.ljust(32, " ") not in dictData:
            print("No password found for " + args.url.strip())
        else:
            print("Password for " + args.url + " is: " + dictData.get(args.url.ljust(32, " ")).strip())