# node/src/node.py
from src.core.blockchain import Blockchain
from src.consensus.pbft import PBFTNode

class Node:
    """
    A singleton class to hold the state of our blockchain node.
    This includes the blockchain itself and the consensus engine.
    """
    def __init__(self, node_id: str):
        print(f"[{node_id}] Initializing Node components...")
        self.blockchain = Blockchain(node_id=node_id)
        self.pbft_node = PBFTNode(node_id=node_id, blockchain=self.blockchain)
        print(f"[{node_id}] Node components initialized.")