# test_sign.py
import sys
sys.path.insert(0, './node/src') # Add path to our crypto module
from crypto.wallet import Wallet, hash_data, sign_data

# --- PASTE YOUR PRIVATE KEY FROM STEP 3 HERE ---
private_key_hex = "01bbd5cfb5395fc197fd42567a01211a0f5856a58def4841d26c9d75822cbf8c"

message_to_sign = "hello"

# Restore the wallet
wallet = Wallet(private_key_bytes=bytes.fromhex(private_key_hex))

# Hash the data
data_hash = hash_data(message_to_sign)

# Sign the hash
signature_hex = sign_data(wallet, data_hash)

print("--- Use these values for the next step ---")
print(f"PublicKey: {wallet.public_key}")
print(f"Message: {message_to_sign}")
print(f"Signature: {signature_hex}")