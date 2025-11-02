# simulator/app.py
import os
import time
import json
import random
import requests
import yaml
import rlp
from ecdsa import SigningKey, SECP256k1
from Crypto.Hash import keccak

# ... (Wallet, hash_data, sign_data, Transaction classes remain IDENTICAL) ...
# --- Crypto & Transaction Classes (Mirrors the node's implementation for compatibility) ---
class Wallet:
    def __init__(self, private_key_bytes=None):
        self.signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1) if private_key_bytes else SigningKey.generate(curve=SECP256k1)
        self.verifying_key = self.signing_key.get_verifying_key()
    @property
    def public_key(self) -> str: return self.verifying_key.to_string('uncompressed').hex()

def hash_data(data: str) -> bytes:
    k = keccak.new(digest_bits=256); k.update(data.encode('utf-8')); return k.digest()
def sign_data(wallet: Wallet, data_hash: bytes) -> str: return wallet.signing_key.sign_digest(data_hash).hex()

class Transaction:
    def __init__(self, sender, to, amount, nonce, data, timestamp=None, signature=None, tx_hash=None):
        self.nonce, self.sender, self.to, self.amount, self.data = nonce, sender, to, amount, data
        self.timestamp = timestamp or int(time.time()); self.signature, self.hash = signature, tx_hash
    def to_dict(self) -> dict: return {"nonce": self.nonce, "from": self.sender, "to": self.to, "amount": self.amount, "data": self.data, "timestamp": self.timestamp, "signature": self.signature, "hash": self.hash}
    def _get_signing_payload(self) -> bytes: return rlp.encode([self.nonce, self.sender.encode('utf-8'), self.to.encode('utf-8'), self.amount, self.data.encode('utf-8'), self.timestamp])
    def sign(self, wallet: Wallet):
        if wallet.public_key != self.sender: raise ValueError("Wallet PK mismatch")
        self.signature = sign_data(wallet, hash_data(self._get_signing_payload().hex()))
        self.hash = self.compute_hash()
    def compute_hash(self) -> str:
        sig = self.signature or ""; full_tx_list = [self.nonce, self.sender.encode('utf-8'), self.to.encode('utf-8'), self.amount, self.data.encode('utf-8'), self.timestamp, sig.encode('utf-8')]
        return hash_data(rlp.encode(full_tx_list).hex()).hex()

# --- Main Simulator Logic ---
def generate_temperature_reading(config):
    temp = random.normalvariate(config['normal_temp'], config['temp_std_dev'])
    if random.random() < config['breach_chance']: temp += random.uniform(5, 10)
    return round(temp, 2)

def get_contract_address(node_url: str) -> str or None:
    """Polls the node's system endpoint to get the deployed contract address."""
    while True:
        try:
            print("Querying node for contract address...")
            response = requests.get(f"{node_url}/system/contract/")
            if response.status_code == 200:
                address = response.json()['contract_address']
                print(f"✅ Got contract address: {address}")
                return address
        except requests.exceptions.ConnectionError:
            pass # Node might not be ready yet, ignore and retry
        
        print("Node not ready or contract not deployed yet. Retrying in 5 seconds...")
        time.sleep(5)

def main():
    print("✅ IoT Simulator started.")
    with open('config.yaml', 'r') as f: config = yaml.safe_load(f)
    sim_config, node_url = config['simulation'], os.environ.get('NODE_URL', config['node_url'])
    print(f"Targeting node URL: {node_url}")
    
    # --- THIS IS THE NEW AUTOMATED LOGIC ---
    contract_address = get_contract_address(node_url)
    if not contract_address:
        print("🛑 Could not retrieve contract address. Shutting down.")
        return

    wallet = Wallet(bytes.fromhex(config['simulator_private_key']))
    print(f"Simulator Wallet Public Key: {wallet.public_key[:10]}...")
    nonce = 0

    while True:
        try:
            # ... The rest of the while loop is IDENTICAL ...
            temperature, reading_timestamp = generate_temperature_reading(sim_config), int(time.time())
            print(f"\n[{time.ctime()}] 🌡️  Generated reading for {sim_config['shipment_id']}: {temperature}°C")
            tx_data = {"method": "record_temperature", "params": {"shipment_id": sim_config['shipment_id'], "temperature": temperature, "timestamp": reading_timestamp}}
            tx = Transaction(sender=wallet.public_key, to=contract_address, amount=0, nonce=nonce, data=json.dumps(tx_data))
            tx.sign(wallet)
            print(f"🖋️  Signing and sending transaction (nonce={nonce}, hash={tx.hash[:10]}...)")
            response = requests.post(f"{node_url}/tx/", json=tx.to_dict(), headers={'Content-Type': 'application/json'})
            if response.status_code == 202:
                print(f"✅ Transaction successfully submitted to mempool: {response.json().get('txHash')}")
                nonce += 1
            else:
                print(f"❌ Error submitting transaction: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        time.sleep(sim_config['interval_seconds'])

if __name__ == "__main__": main()