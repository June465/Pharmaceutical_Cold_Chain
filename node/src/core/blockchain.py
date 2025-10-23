# node/src/core/blockchain.py
from typing import Optional
from src.core.block import Block
from src.db.database import Database

class Blockchain:
    def __init__(self, node_id: str):
        self.db = Database(node_id)
        self._initialize_chain()

    def _initialize_chain(self):
        """Creates the genesis block if the chain is empty."""
        head_block = self.db.get_head_block()
        if not head_block:
            print("No existing blockchain found. Creating genesis block...")
            genesis_block = Block(
                index=0,
                prev_hash="0" * 64, # 64 zeros
                proposer_id="genesis"
            )
            self.db.save_block(genesis_block)

    def get_head(self) -> Optional[Block]:
        return self.db.get_head_block()
    
    def add_block(self, block: Block) -> bool:
        """Validates and adds a new block to the chain."""
        head_block = self.get_head()
        if head_block:
            # Basic validation
            if block.header['index'] != head_block.header['index'] + 1:
                print("Error: New block index is invalid.")
                return False
            if block.header['prevHash'] != head_block.hash:
                print("Error: New block's prevHash does not match head.")
                return False
        
        self.db.save_block(block)
        return True

    def get_block_by_height(self, height: int) -> Optional[Block]:
        return self.db.get_block_by_height(height)

    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        return self.db.get_block_by_hash(block_hash)