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
            "merkleRoot": self.compute_merkle_root(), # <-- RENAMED for consistency
            "stateRoot": None, # <-- ADDED: Placeholder for the state root from the VM
            "timestamp": timestamp or int(time.time()),
            "proposerId": proposer_id
        }
        self.hash = block_hash or self.compute_hash()

    def compute_merkle_root(self) -> str: # <-- RENAMED: This is the primary fix for the error
        """Calculates the Merkle root of the block's transactions."""
        tx_hashes = [tx.hash for tx in self.transactions]
        return build_merkle_root(tx_hashes)

    def compute_hash(self) -> str:
        """Computes the hash of the block header."""
        header_string = json.dumps(self.header, sort_keys=True)
        return hash_data(header_string).hex()
    
    def recompute_hash(self): # <-- ADDED: A helper method for when the header changes
        """Re-calculates the block's hash. Needed after state root is added."""
        self.hash = self.compute_hash()
    
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
            # Create a full Transaction object from the dictionary
            tx = Transaction.from_dict(tx_data) if hasattr(Transaction, 'from_dict') else Transaction(
                sender=tx_data.get('from'), 
                to=tx_data.get('to'),
                amount=tx_data.get('amount'),
                nonce=tx_data.get('nonce'),
                data=tx_data.get('data', ""),
                timestamp=tx_data.get('timestamp'),
                signature=tx_data.get('signature'),
                tx_hash=tx_data.get('hash')
            )
            transactions.append(tx)

        block = cls(
            index=data['header']['index'],
            prev_hash=data['header']['prevHash'],
            proposer_id=data['header']['proposerId'],
            transactions=transactions,
            timestamp=data['header']['timestamp'],
            block_hash=data['hash']
        )
        # Manually set the state root if it exists in the data
        block.header['stateRoot'] = data['header'].get('stateRoot')
        return block