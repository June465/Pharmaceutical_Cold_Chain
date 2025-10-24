# node/src/core/blockchain.py
from .block import Block
from ..db.database import Database 
from ..state.world_state import WorldState
from ..vm.executor import execute_transaction

class Blockchain:
    def __init__(self, node_id: str):
        self.db = Database(node_id)
        self.world_state = WorldState(self.db)
        self._initialize_chain()

    def _initialize_chain(self):
        if not self.db.get_head_block():
            print("No existing blockchain found. Creating genesis block...")
            genesis_block = Block(index=0, prev_hash="0" * 64, proposer_id="genesis")
            self.db.save_block(genesis_block)

    def get_head(self):
        return self.db.get_head_block()
    
    def add_block(self, block: Block):
        head_block = self.get_head()
        if head_block and (block.header['index'] != head_block.header['index'] + 1 or block.header['prevHash'] != head_block.hash):
            return False
        
        for tx in block.transactions:
            execute_transaction(tx, self.world_state)
        
        self.db.save_block(block)
        return True

    def get_block_by_height(self, height: int):
        return self.db.get_block_by_height(height)