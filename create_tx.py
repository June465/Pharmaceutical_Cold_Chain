# create_tx.py
import sys
import json
import requests # We'll use the requests library to send the transaction

# Add the 'src' directory to the path to find our modules
sys.path.insert(0, './node/src')
sys.path.insert(0, './node')
from src.crypto.wallet import Wallet
from src.core.transaction import Transaction

# --- PASTE YOUR WALLET DETAILS FROM THE PREVIOUS STEP HERE ---
private_key_hex = "4c9dcfe5acb0f1f7db7047f0afbe5b35af06db907e4a36887cab8547175c4e0f"
sender_public_key = "04304031f9c405181f3d4fee34e1899068f9116cb5de6a501d1f6c932cc22463537d55a28c7d93be5ab7ea2e421a138f1c2d5735c6f10e384a96fc4621ea1d4618"
# ---

# Create the wallet object to sign with
wallet = Wallet(private_key_bytes=bytes.fromhex(private_key_hex))

# 1. Create the transaction object
tx = Transaction(
    sender=sender_public_key,
    to="0xRECIPIENT_ADDRESS_HERE", # Just a placeholder address
    amount=100,
    nonce=1
)

# 2. Sign the transaction
tx.sign(wallet)

# 3. Get the transaction data as a dictionary
tx_data = tx.to_dict()

print("--- Signed Transaction ---")
print(json.dumps(tx_data, indent=2))

# 4. Send it to a node
node_url = "http://localhost:8001/tx"
print(f"\nSubmitting transaction to {node_url}...")

try:
    response = requests.post(node_url, json=tx_data)
    response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
    
    print("--- Node Response ---")
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Error submitting transaction: {e}")
    print("Response body:", e.response.text if e.response else "No response")