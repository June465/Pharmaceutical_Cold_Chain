# node/src/db/database.py
import os
import plyvel
import json
from ..core.block import Block

class Database:
    def __init__(self, node_id: str):
        db_path = f"data/{node_id}_chain"
        os.makedirs(db_path, exist_ok=True)
        self.db = plyvel.DB(db_path, create_if_missing=True)
        self.BLOCK_PREFIX = b'block:'
        self.INDEX_PREFIX = b'index:'
        self.HEAD_HASH_KEY = b'head_hash'

    def save_block(self, block: Block):
        block_hash_bytes = bytes.fromhex(block.hash)
        with self.db.write_batch() as wb:
            wb.put(self.BLOCK_PREFIX + block_hash_bytes, json.dumps(block.to_dict()).encode('utf-8'))
            wb.put(self.INDEX_PREFIX + str(block.header['index']).encode(), block_hash_bytes)
            wb.put(self.HEAD_HASH_KEY, block_hash_bytes)
        print(f" Saved block {block.header['index']} with hash {block.hash[:10]}...")

    def get_block_by_hash(self, block_hash: str):
        block_data = self.db.get(self.BLOCK_PREFIX + bytes.fromhex(block_hash))
        return Block.from_dict(json.loads(block_data.decode('utf-8'))) if block_data else None

    def get_block_by_height(self, height: int):
        block_hash_bytes = self.db.get(self.INDEX_PREFIX + str(height).encode())
        return self.get_block_by_hash(block_hash_bytes.hex()) if block_hash_bytes else None

    def get_head_block(self):
        head_hash_bytes = self.db.get(self.HEAD_HASH_KEY)
        return self.get_block_by_hash(head_hash_bytes.hex()) if head_hash_bytes else None