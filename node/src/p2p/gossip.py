# node/src/p2p/gossip.py
import os
import requests
from threading import Thread

# This import is needed for type hinting, but since it causes a circular
# dependency if imported at the top level, we'll manage it inside the function.
# from src.core.transaction import Transaction 

# Read the list of peers from the environment variable
PEERS = os.environ.get('PEERS', '').split(',')
# Filter out any empty strings that might result from a trailing comma
PEERS = [peer for peer in PEERS if peer]

# --- Existing Function (Slightly Improved) ---
def broadcast_transaction(tx): # Type hint removed to avoid circular import
    """
    Broadcasts a transaction to all peers in the network.
    This is done in a separate thread to not block the main API response.
    """
    print(f" gossiping transaction {tx.hash[:10]}... to {len(PEERS)} peers.")
    thread = Thread(target=_send_transaction_to_peers, args=(tx,))
    thread.start()

def _send_transaction_to_peers(tx):
    """The actual function that sends the transaction to each peer."""
    tx_data = tx.to_dict()

    for peer in PEERS:
        # Improved: Use the full, explicit URL for clarity and robustness
        url = f"http://{peer}:8000/gossip/tx"
        try:
            response = requests.post(url, json=tx_data, timeout=2)
            if response.status_code == 200:
                print(f"  -> Successfully sent tx {tx.hash[:10]} to {peer}")
            else:
                print(f"  -> Peer {peer} responded with {response.status_code} for tx {tx.hash[:10]}")
        except requests.exceptions.RequestException as e:
            print(f"  -> Failed to send tx to {peer}. Error: {e}")

# --- NEW FUNCTION THAT WAS MISSING ---
def broadcast_message(message: dict, endpoint: str):
    """
    Broadcasts a generic message (dict) to all peers on a specific endpoint.
    Used for consensus messages. Runs in a background thread.
    This is the function that was missing.
    """
    msg_type = message.get('type', 'Unknown')
    print(f" gossiping {msg_type} message to {len(PEERS)} peers.")
    thread = Thread(target=_send_message_to_peers, args=(message, endpoint))
    thread.start()

def _send_message_to_peers(message: dict, endpoint: str):
    """The actual worker function that sends a generic message."""
    for peer in PEERS:
        url = f"http://{peer}:8000{endpoint}"  # e.g., http://node2:8000/gossip/consensus
        try:
            response = requests.post(url, json=message, timeout=2)
            if response.status_code == 200:
                print(f"  -> Successfully sent {message.get('type')} to {peer}")
            else:
                print(f"  -> Peer {peer} responded to {message.get('type')} with {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  -> Failed to send message to {peer}. Error: {e}")

             