# node/src/core/block.py
import time
import json
from typing import List, Dict 
from src.core.transaction import Transaction
from src.core.merkle import build_merkle_root
from src.crypto.wallet import hash_data

class Block:
    def __init__(self,
                 index: int,
                 prev_hash: str,
                 proposer_id: str,
                 transactions: List[Transaction] = None,
                 timestamp: int = None,
                 block_hash: str = None):
        
        self.transactions = transactions or []
        self.header = {
            "index": index,
            "prevHash": prev_hash,
            "merkleRoot": self.calculate_merkle_root(),
            "timestamp": timestamp or int(time.time()),
            "proposerId": proposer_id
        }
        self.hash = block_hash or self.compute_hash()

    def calculate_merkle_root(self) -> str:
        """Calculates the Merkle root of the block's transactions."""
        tx_hashes = [tx.hash for tx in self.transactions]
        return build_merkle_root(tx_hashes)

    def compute_hash(self) -> str:
        """Computes the hash of the block header."""
        # We use json.dumps with sorted_keys for a deterministic hash
        header_string = json.dumps(self.header, sort_keys=True)
        return hash_data(header_string).hex()
    
    def to_dict(self) -> Dict:
        """Serializes the block to a dictionary."""
        return {
            "hash": self.hash,
            "header": self.header,
            "transactions": [tx.to_dict() for tx in self.transactions]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Block':
        """Deserializes a dictionary into a Block object."""
        transactions = []
        for tx_data in data['transactions']:
            transactions.append(Transaction(
                sender=tx_data['from'], 
                to=tx_data['to'],
                amount=tx_data['amount'],
                nonce=tx_data['nonce'],
                data=tx_data.get('data', ""),
                timestamp=tx_data['timestamp'],
                signature=tx_data['signature'],
                tx_hash=tx_data['hash'] 
            ))
        block = cls(
            index=data['header']['index'],
            prev_hash=data['header']['prevHash'],
            proposer_id=data['header']['proposerId'],
            transactions=transactions,
            timestamp=data['header']['timestamp'],
            block_hash=data['hash']
        )
        return block