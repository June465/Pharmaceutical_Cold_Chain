# node/src/core/blockchain.py
from typing import Optional
from src.core.block import Block
from src.db.database import Database
from src.core.mempool import Mempool
from src.state.world_state import WorldState
from src.vm.executor import execute_transaction
from src.consensus.pbft import PBFTNode
from src.utils.logger import get_logger
from src.core.transaction import Transaction # Import Transaction

log = get_logger(__name__)

class Blockchain:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.db = Database(node_id)
        self.mempool = Mempool()
        self.world_state = WorldState(self.db)
        self.pbft_node = PBFTNode(self.node_id, self)
        self.pharma_contract_address = None # <-- ADD THIS
        self._initialize_chain()

    def _initialize_chain(self):
        """Creates genesis block AND deploys the core PharmaContract."""
        head_block = self.db.get_head_block()
        if not head_block:
            log.info("No existing blockchain found. Creating genesis state...")
            
            # 1. Create a "genesis deployment transaction"
            deployment_tx = Transaction(
                sender='0x_genesis_deployer', to='0x0', amount=0, nonce=0,
                data='PharmaContract', signature='genesis_signature'
            )
            deployment_tx.hash = deployment_tx.compute_hash()

            # 2. Directly execute this transaction to deploy the contract
            try:
                execute_transaction(deployment_tx, self.world_state)
                # Get the address
                self.pharma_contract_address = self.world_state.create_contract_address(deployment_tx)
                log.info(f"Genesis contract 'PharmaContract' deployed to {self.pharma_contract_address}")
            except Exception as e:
                log.error(f"CRITICAL: Genesis contract deployment failed: {e}")
                return

            # 3. Create the genesis block
            genesis_block = Block(index=0, prev_hash="0" * 64, proposer_id="genesis")
            
            # 4. Save the state root from the deployment into the genesis block
            self.world_state.update_state_root(genesis_block.header)
            self.db.save_block(genesis_block)
            log.info(f"Genesis block created successfully with stateRoot: {genesis_block.header['stateRoot']}")
        else:
            # If chain exists, we need to find the contract address
            self.pharma_contract_address = self.world_state.find_contract_address_by_name("PharmaContract")
            if self.pharma_contract_address:
                log.info(f"Found existing PharmaContract at {self.pharma_contract_address}")
            else:
                log.warning("Blockchain exists but could not find PharmaContract address.")

    # ... (rest of the file is IDENTICAL to the last working version) ...
    def get_head(self) -> Optional[Block]: return self.db.get_head_block()
    def add_block(self, block: Block) -> bool:
        head_block = self.get_head()
        if head_block and (block.header['index'] != head_block.header['index'] + 1 or block.header['prevHash'] != head_block.hash):
            log.error("Invalid block: index or prevHash mismatch.")
            return False
        log.info(f"Executing {len(block.transactions)} transactions for new block...")
        for tx in block.transactions:
            try: execute_transaction(tx, self.world_state)
            except Exception as e: log.error(f"Transaction execution failed for tx {tx.hash}: {e}"); return False
        self.world_state.update_state_root(block.header)
        block.recompute_hash() 
        log.info(f"New state root for block {block.header['index']}: {block.header['stateRoot']}")
        self.db.save_block(block)
        log.info(f"🔗 Added new block #{block.header['index']} to the chain with hash {block.hash[:10]}")
        for tx in block.transactions: self.mempool.remove_transaction(tx.hash)
        return True
    def get_block_by_height(self, height: int) -> Optional[Block]: return self.db.get_block_by_height(height)
    def get_block_by_hash(self, block_hash: str) -> Optional[Block]: return self.db.get_block_by_hash(block_hash)