from phe import paillier
from sslib import shamir



class PaillierKeyManager:
    def __init__(self, key_length=4096):
        self.key_length = key_length
        self.public_key = None
        self.private_key = None

    def generate_keys(self):
        # Generate public and private keys
        self.public_key, self.private_key = paillier.generate_paillier_keypair(n_length=self.key_length)
        print("generated keys")
        print(self.public_key)
        return self.public_key, self.private_key


    def encrypt_votes(self, votes):
        return [self.public_key.encrypt(v) for v in votes]

    

    
    def split_private_key(self, threshold, num_shares):
        p = self.private_key.p
        q = self.private_key.q

        # Get the bytes. (Round the lenght)
        p_bytes = p.to_bytes((p.bit_length() + 7) // 8, 'big')
        q_bytes = q.to_bytes((q.bit_length() + 7) // 8, 'big')

        p_length = len(p_bytes)
        q_length = len(q_bytes)


        secret = p_length.to_bytes(4, 'big') + p_bytes + q_length.to_bytes(4, 'big') + q_bytes

        # Split the secret
        secret_data = shamir.split_secret(secret, threshold, num_shares)
        # secret_data contains: required_shares, prime_mod, shares
        return secret_data 


    def reconstruct_private_key(self, secret_data):
        # Ricostruisci il segreto dalle condivisioni
        secret = shamir.recover_secret(secret_data)

        # Estrai p_length e q_length
        p_length = int.from_bytes(secret[:4], 'big')
        p_bytes = secret[4:4 + p_length]

        q_length_start = 4 + p_length
        q_length = int.from_bytes(secret[q_length_start:q_length_start + 4], 'big')
        q_bytes = secret[q_length_start + 4:q_length_start + 4 + q_length]

        # Converti bytes in interi
        p = int.from_bytes(p_bytes, 'big')
        q = int.from_bytes(q_bytes, 'big')

        # Ricostruisci le chiavi
        n = p * q
        self.public_key = paillier.PaillierPublicKey(n)
        self.private_key = paillier.PaillierPrivateKey(self.public_key, p, q)
        return self.private_key

    def decrypt_votes(self, encrypted_votes):
        # Decifra i voti utilizzando la chiave privata
        return [self.private_key.decrypt(e) for e in encrypted_votes]













    """def save_keys(self, public_key_file='public.key', private_key_file='private.key'):
        # Save the public key
        with open(public_key_file, 'w') as f:
            f.write(str(self.public_key.n))

        # Save the private key
        with open(private_key_file, 'w') as f:
            f.write(f"{self.private_key.p},{self.private_key.q}")

    def load_public_key(self, public_key_file='public.key'):
        with open(public_key_file, 'r') as f:
            n = int(f.read())
        self.public_key = paillier.PaillierPublicKey(n)
        return self.public_key

    def load_private_key(self, private_key_file='private.key'):
        with open(private_key_file, 'r') as f:
            p_str, q_str = f.read().split(',')
            p = int(p_str)
            q = int(q_str)
        self.public_key = paillier.PaillierPublicKey(p * q)
        self.private_key = paillier.PaillierPrivateKey(self.public_key, p, q)
        return self.private_key"""
