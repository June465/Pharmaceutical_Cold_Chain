from .core.blockchain import Blockchain
from .consensus.pbft import PBFTNode

class Node:
    def __init__(self, node_id: str):
        print(f"[{node_id}] Initializing Node components...")
        self.blockchain = Blockchain(node_id=node_id)
        self.pbft_node = PBFTNode(node_id=node_id, blockchain=self.blockchain)
        print(f"[{node_id}] Node components initialized.")