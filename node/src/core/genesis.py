# node/src/core/genesis.py
from src.core.block import Block

# A fixed, deterministic timestamp for the genesis block (e.g., Jan 1, 2023)
# This ensures every node creates the exact same genesis block hash.
GENESIS_BLOCK_TIMESTAMP = 1672531200

def create_genesis_block():
    """Creates the one and only genesis block for the entire blockchain."""
    return Block(
        index=0,
        prev_hash="0" * 64,
        proposer_id="genesis",
        timestamp=GENESIS_BLOCK_TIMESTAMP,
        transactions=[] # The genesis block has no transactions
    )