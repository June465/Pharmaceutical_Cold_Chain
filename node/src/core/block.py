# node/src/core/block.py
import time
import json
from .transaction import Transaction
from .merkle import build_merkle_root
from ..crypto.wallet import hash_data

class Block:
    def __init__(self, index, prev_hash, proposer_id, transactions=None, timestamp=None, block_hash=None):
        self.transactions = transactions or []
        self.header = {
            "index": index,
            "prevHash": prev_hash,
            "merkleRoot": self.calculate_merkle_root(),
            "timestamp": timestamp or int(time.time()),
            "proposerId": proposer_id
        }
        self.hash = block_hash or self.compute_hash()

    def calculate_merkle_root(self):
        tx_hashes = [tx.hash for tx in self.transactions]
        return build_merkle_root(tx_hashes)

    def compute_hash(self):
        header_string = json.dumps(self.header, sort_keys=True)
        return hash_data(header_string).hex()
    
    def to_dict(self):
        return {"hash": self.hash, "header": self.header, "transactions": [tx.to_dict() for tx in self.transactions]}

    @classmethod
    def from_dict(cls, data):
        transactions = [Transaction.from_dict(tx_data) for tx_data in data['transactions']]
        return cls(index=data['header']['index'], prev_hash=data['header']['prevHash'],
                   proposer_id=data['header']['proposerId'], transactions=transactions,
                   timestamp=data['header']['timestamp'], block_hash=data['hash'])