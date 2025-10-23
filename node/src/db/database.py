# node/src/db/database.py
import os
import plyvel
import json
from typing import Optional
from src.core.block import Block

class Database:
    def __init__(self, node_id: str):
        # Each node will have its own database directory
        db_path = f"data/{node_id}_chain"
        os.makedirs(db_path, exist_ok=True)
        self.db = plyvel.DB(db_path, create_if_missing=True)
        
        # Key prefixes to organize data
        self.BLOCK_PREFIX = b'block:'
        self.INDEX_PREFIX = b'index:'
        self.HEAD_HASH_KEY = b'head_hash'

    def save_block(self, block: Block):
        """Saves a block and updates the chain index."""
        block_hash_bytes = bytes.fromhex(block.hash)
        block_data = json.dumps(block.to_dict()).encode('utf-8')
        
        with self.db.write_batch() as wb:
            # Store the block by its hash: block:<hash> -> block_data
            wb.put(self.BLOCK_PREFIX + block_hash_bytes, block_data)
            # Store the height-to-hash mapping: index:<height> -> hash
            wb.put(self.INDEX_PREFIX + str(block.header['index']).encode(), block_hash_bytes)
            # Update the head hash pointer
            wb.put(self.HEAD_HASH_KEY, block_hash_bytes)
        print(f" Saved block {block.header['index']} with hash {block.hash[:10]}...")

    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        """Retrieves a block by its hash."""
        block_data = self.db.get(self.BLOCK_PREFIX + bytes.fromhex(block_hash))
        if block_data:
            return Block.from_dict(json.loads(block_data.decode('utf-8')))
        return None

    def get_block_by_height(self, height: int) -> Optional[Block]:
        """Retrieves a block by its height."""
        block_hash_bytes = self.db.get(self.INDEX_PREFIX + str(height).encode())
        if block_hash_bytes:
            return self.get_block_by_hash(block_hash_bytes.hex())
        return None

    def get_head_block(self) -> Optional[Block]:
        """Retrieves the latest block in the chain."""
        head_hash_bytes = self.db.get(self.HEAD_HASH_KEY)
        if head_hash_bytes:
            return self.get_block_by_hash(head_hash_bytes.hex())
        return None
        
    def close(self):
        self.db.close()