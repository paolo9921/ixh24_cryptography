from contract_manager import ContractManager
from crypto_manager import PaillierKeyManager


def main():
    try:
        # Deploy contract
        contract_manager = ContractManager()
        contract_address = contract_manager.deploy_contract()
        print(f"\nContract deployed at address: {contract_address}")

        n_uni = int(input("\nEnter the number of univeristies: "))
        if n_uni <= 0:
            raise ValueError("The number must be positive")

        # Initialize data structures to hold university data
        unis = {}

        # Submit votes for each university
        for i in range(n_uni):
            uni_id = int(input(f"\nEnter the ID for university {i+1}: "))
            votes = list(map(int, input("Enter the votes (space-separated): ").strip().split()))
            receipt = contract_manager.submit_votes(uni_id, votes)
            print(f"Votes submitted for university {uni_id}")
            unis[uni_id] = {
                'votes': votes,
                'encrypted_votes': None,
                'share': None
            }

        # Generate keys
        key_manager = PaillierKeyManager()
        key_manager.generate_keys()
        num_shares = n_uni
        threshold = n_uni // 2 + 1

        # Split the private key into shares
        secret_data = key_manager.split_private_key(threshold, num_shares)
        print(f"Private key split into {num_shares} shares with threshold {threshold}")

        shares = secret_data['shares']

        # STEP 1
        # Every universities receive the encrypted votes and his share
        for i, uni_id in enumerate(unis.keys()):

            # Encrypt the votes for the university
            votes = contract_manager.get_votes(uni_id)
            encrypted_votes = key_manager.encrypt_votes(votes)
            unis[uni_id]['encrypted_votes'] = encrypted_votes

            unis[uni_id]['share'] = shares[i]

            print(f"\nUniversity {uni_id} received its encrypted votes and share.")


        # STEP 2
        # The president receives all the encrypted votes and mulitply them to obtain result of election
        president_collection = None

        for i in unis.keys():
            encrypt_votes = unis[i]['encrypted_votes']

            for enc_vote in encrypt_votes:
                if president_collection is None:
                    president_collection = enc_vote.ciphertext()
                else:
                    # Since encrypted_votes is phe.EncryptedNumber, the + is the homomorphic addiction
                    president_collection = president_collection + enc_vote

        print("\nPresident has calculated the encrypted result of all votes.")

        # STEP 3

        collected_shares = []
        for i in unis.keys():
            
            share = unis[i]['share']
            collected_shares.append(share)
            if len(collected_shares) >= threshold:
                break

        collected_secret_data = {
            'required_shares': secret_data['required_shares'],
            'prime_mod': secret_data['prime_mod'],
            'shares': collected_shares
        }

        # Reconstruct the private key
        key_manager.reconstruct_private_key(collected_secret_data)
        print("\nPrivate key successfully reconstructed from university shares.")

        # Decrypt the votes
        print("\nDecrypting votes for each university:")
        for uni_id in unis.keys():
            encrypted_votes = unis[uni_id]['encrypted_votes']
            decrypted_votes = key_manager.decrypt_votes(encrypted_votes)
            print(f"University {uni_id}: Decrypted votes: {decrypted_votes}")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
