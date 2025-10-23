import os
import json
import time
from web3 import Web3
from dotenv import load_dotenv

# --- Load Configuration from .env file ---
load_dotenv()
GANACHE_RPC_URL = os.getenv("GANACHE_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
ORACLE_PRIVATE_KEY = os.getenv("ORACLE_PRIVATE_KEY")
if not ORACLE_PRIVATE_KEY:
    print("Error: ORACLE_PRIVATE_KEY not found in .env file.")
    exit()

# --- Web3 Setup ---
w3 = Web3(Web3.HTTPProvider(GANACHE_RPC_URL))
if not w3.is_connected():
    print(f"Failed to connect to Ganache at {GANACHE_RPC_URL}")
    exit()
print(f"Successfully connected to Ganache.")

# --- DERIVE ORACLE ADDRESS (MOVED HERE) ---
# Now that we have a 'w3' instance, we can derive the public address
try:
    ORACLE_ADDRESS = w3.eth.account.from_key(ORACLE_PRIVATE_KEY).address
except Exception as e:
    print(f"Error deriving address from private key: {e}")
    print("Please ensure ORACLE_PRIVATE_KEY in your .env file is correct and does NOT have a '0x' prefix.")
    exit()


# --- Load Contract ABI ---
try:
    with open('abi.json', 'r') as f:
        contract_info = json.load(f)
        CONTRACT_ABI = contract_info['abi']
except FileNotFoundError:
    print("Error: abi.json not found. Make sure it's in the same directory.")
    exit()
except KeyError:
    print("Error: 'abi' key not found in abi.json. Make sure the file format is correct.")
    exit()


# --- Contract Instance ---
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
print(f"Connected to ColdChain contract at address: {CONTRACT_ADDRESS}")

# --- Simulation Data ---
SHIPMENT_ID = "SHIP001"
TEMPERATURE_DATA = [
    {"temp": 5, "location": "Warehouse A"},
    {"temp": 6, "location": "On Truck #123"},
    {"temp": 7, "location": "On Truck #123"},
    {"temp": 9, "location": "Highway Stop (Hot)"},  # <-- BREACH (above 8°C)
    {"temp": 8, "location": "On Truck #123"},
    {"temp": 1, "location": "Mountain Pass (Cold)"}, # <-- BREACH (below 2°C)
    {"temp": 4, "location": "Receiving Dock"}
]
INTERVAL_SECONDS = 5

def send_temperature_update(shipment_id, current_temp, location):
    """Builds, signs, and sends a transaction to the updateTemperature function."""
    print(f"\n---> Sending Temp Update for '{shipment_id}': {current_temp}°C at '{location}'")
    
    try:
        nonce = w3.eth.get_transaction_count(ORACLE_ADDRESS)
        txn_dict = contract.functions.updateTemperature(
            shipment_id,
            current_temp,
            location
        ).build_transaction({
            'chainId': w3.eth.chain_id,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce
        })

        signed_txn = w3.eth.account.sign_transaction(txn_dict, private_key=ORACLE_PRIVATE_KEY)
        
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"Transaction sent! Hash: {tx_hash.hex()}")
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction confirmed in block number: {receipt.blockNumber}")
        if receipt.status == 0:
            print("Transaction FAILED! Check contract logic or parameters.")
        else:
            print("Transaction successful.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("This could be because the shipment ID doesn't exist yet (create it from the DApp first) or a contract revert.")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("          IoT Oracle Simulator Started")
    print("="*50)
    print(f"Oracle Address: {ORACLE_ADDRESS}")
    print(f"Simulating for Shipment ID: '{SHIPMENT_ID}'")
    print(f"NOTE: You must create this shipment from the DApp (as the Manufacturer) before this script can update it.")
    
    input("\n>>> Press Enter to start sending temperature data once the shipment is created in the DApp... <<<\n")

    for data in TEMPERATURE_DATA:
        send_temperature_update(SHIPMENT_ID, data["temp"], data["location"])
        print(f"Waiting for {INTERVAL_SECONDS} seconds...")
        time.sleep(INTERVAL_SECONDS)

    print("\n" + "="*50)
    print("          IoT Oracle simulation complete.")
    print("="*50)