# node/src/p2p/gossip.py
import os
import requests
from threading import Thread
from src.core.transaction import Transaction

# Read the list of peers from the environment variable
PEERS = os.environ.get('PEERS', '').split(',')
# Filter out any empty strings that might result from a trailing comma
PEERS = [peer for peer in PEERS if peer]

def broadcast_transaction(tx: Transaction):
    """
    Broadcasts a transaction to all peers in the network.
    This is done in a separate thread to not block the main API response.
    """
    print(f" gossiping transaction {tx.hash[:10]}... to {len(PEERS)} peers.")
    
    # We use a thread so the user gets a fast response from the API,
    # while the broadcast happens in the background.
    thread = Thread(target=_send_to_peers, args=(tx,))
    thread.start()

def _send_to_peers(tx: Transaction):
    """The actual function that sends the transaction to each peer."""
    tx_data = tx.to_dict()

    for peer in PEERS:
        url = f"{peer}/gossip/tx"
        try:
            # We expect a 202 Accepted response. Timeout is important.
            response = requests.post(url, json=tx_data, timeout=2)
            if response.status_code == 202:
                print(f"  -> Successfully sent tx {tx.hash[:10]} to {peer}")
            else:
                # The peer might already have the tx, which is okay.
                print(f"  -> Peer {peer} responded with {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"  -> Failed to send tx to {peer}. Error: {e}")