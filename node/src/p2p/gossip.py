# node/src/p2p/gossip.py
import os
import requests
from threading import Thread

PEERS = [peer for peer in os.environ.get('PEERS', '').split(',') if peer]

def broadcast_transaction(tx):
    Thread(target=_send_to_peers, args=(tx.to_dict(), "/gossip/tx")).start()

def broadcast_message(msg):
    Thread(target=_send_to_peers, args=(msg, "/gossip/consensus")).start()

def _send_to_peers(payload, endpoint):
    for peer in PEERS:
        try:
            requests.post(f"{peer}{endpoint}", json=payload, timeout=2)
        except requests.exceptions.RequestException as e:
            print(f"  -> Failed to send to {peer}. Error: {e}")