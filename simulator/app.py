import os
import time
import json
import random
import yaml
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.exceptions import ContractLogicError # Import for preflight check

# --- 1. SETUP AND CONFIGURATION ---
print("✅ IoT Simulator for PharmaChain contract started.")

# ... (This entire setup section is correct from our last version)
script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

ALCHEMY_URL = os.getenv("ALCHEMY_URL")
PRIVATE_KEY = os.getenv("SIMULATOR_PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
SHIPMENT_ID = os.getenv("SHIPMENT_ID", "SHIP-001")

if not all([ALCHEMY_URL, PRIVATE_KEY, CONTRACT_ADDRESS]):
    raise Exception("Please set ALCHEMY_URL, SIMULATOR_PRIVATE_KEY, and CONTRACT_ADDRESS in the root .env file.")

abi_path = os.path.join(script_dir, '..', 'explorer', 'src', 'abis', 'PharmaChain.json')
config_path = os.path.join(script_dir, 'config.yaml')

with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
sim_config = config['simulation']

try:
    with open(abi_path, 'r', encoding='utf-8') as f:
        abi_data = json.load(f)
        CONTRACT_ABI = abi_data if isinstance(abi_data, list) else abi_data.get('abi')
except FileNotFoundError:
    raise Exception(f"ABI file not found at {abi_path}.")

if not CONTRACT_ABI:
    raise Exception(f"Could not find ABI array in {abi_path}.")

# --- 2. CONNECT TO ETHEREUM NETWORK ---
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0) 

if not w3.is_connected():
    raise ConnectionError("🛑 Error: Could not connect to Ethereum node.")

print(f"Connected to Ethereum chain ID: {w3.eth.chain_id}")

# --- 3. LOAD WALLET AND CONTRACT ---
account = w3.eth.account.from_key(PRIVATE_KEY)
wallet_address = account.address
print(f"Loaded simulator wallet: {wallet_address}")

pharma_contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# --- 4. SIMULATOR LOGIC ---
def generate_temperature_reading(config):
    # ... (this function is correct)
    temp = random.normalvariate(config['normal_temp'], config['temp_std_dev'])
    if random.random() < config['breach_chance']:
        temp += random.uniform(5, 10)
    return temp

def main():
    print(f"Starting temperature simulation for Shipment ID: {SHIPMENT_ID}")
    while True:
        try:
            temperature = generate_temperature_reading(sim_config)
            temp_scaled = int(temperature * 100)
            print(f"\n[{time.ctime()}] 🌡️  Generated reading: {temperature:.2f}°C (Scaled: {temp_scaled})")

            # --- THIS IS YOUR PREFLIGHT CHECK ---
            try:
                # Simulate the transaction call to check for reverts
                pharma_contract.functions.recordTemperature(
                    SHIPMENT_ID,
                    temp_scaled
                ).call({'from': wallet_address})
                print("✅ Preflight check passed. Proceeding to send transaction...")
            except ContractLogicError as e:
                print("❌ Preflight check FAILED. The transaction will revert.")
                print(f"   Reason from contract: {e}")
                # Wait for the next interval before trying again
                time.sleep(sim_config['interval_seconds'])
                continue # Skip the rest of the loop
            
            # --- Build, Sign, and Send the Transaction ---
            print("Building transaction...")
            nonce = w3.eth.get_transaction_count(wallet_address)
            tx_data = pharma_contract.functions.recordTemperature(
                SHIPMENT_ID, temp_scaled
            ).build_transaction({
                'chainId': w3.eth.chain_id,
                'gas': 200000,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            })
            
            signed_tx = w3.eth.account.sign_transaction(tx_data, private_key=PRIVATE_KEY)
            
            print("Sending transaction to the network...")
            # Use .raw if available (web3.py v6+), otherwise fallback for safety
            raw_tx = signed_tx.raw if hasattr(signed_tx, 'raw') else signed_tx.raw_transaction
            tx_hash = w3.eth.send_raw_transaction(raw_tx)
            
            # --- THIS IS YOUR ETHERSCAN LINK FIX ---
            tx_hash_hex = Web3.to_hex(tx_hash)
            print(f"Transaction sent! Hash: {tx_hash_hex}. Waiting for confirmation...")
            
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
            
            if tx_receipt.status == 1:
                print(f"✅ Transaction confirmed in block: {tx_receipt.blockNumber}")
                print(f"   View on Etherscan: https://sepolia.etherscan.io/tx/{tx_hash_hex}")
            else:
                print(f"❌ Transaction FAILED (reverted) in block: {tx_receipt.blockNumber}")
                print(f"   View on Etherscan: https://sepolia.etherscan.io/tx/{tx_hash_hex}")

        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")

        time.sleep(sim_config['interval_seconds'])

if __name__ == "__main__":
    main()