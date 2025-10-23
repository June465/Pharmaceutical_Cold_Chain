# node/src/core/mempool.py
from typing import List, Dict
from .transaction import Transaction

class Mempool:
    def __init__(self):
        # A simple dictionary to store transactions, keyed by their hash
        self.transactions: Dict[str, Transaction] = {}
    
    def add_transaction(self, tx: Transaction) -> (bool, str):
        """
        Adds a transaction to the mempool after validation.
        """
        # Rule 1: Check for duplicates
        if tx.hash in self.transactions:
            return False, "Duplicate transaction"
        
        # Rule 2: Verify the signature
        if not tx.verify():
            return False, "Invalid signature"

        # More rules will be added later (e.g., nonce check, size limits)
        
        self.transactions[tx.hash] = tx
        print(f"✅ Transaction {tx.hash[:10]}... added to mempool.")
        return True, "Transaction added"

    def get_transactions(self) -> List[Transaction]:
        """Returns all transactions currently in the mempool."""
        return list(self.transactions.values())

    def get_transaction_by_hash(self, tx_hash: str) -> Transaction:
        """Returns a single transaction by its hash."""
        return self.transactions.get(tx_hash)

    def clear(self):
        """Clears all transactions from the mempool."""
        self.transactions.clear()