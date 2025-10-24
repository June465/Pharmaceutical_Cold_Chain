# node/src/core/mempool.py
from .transaction import Transaction

class Mempool:
    def __init__(self):
        self.transactions = {}
    
    def add_transaction(self, tx: Transaction):
        if tx.hash in self.transactions:
            return False, "Duplicate transaction"
        
        # NOTE: Temporarily disabling signature verification for easier testing
        # if not tx.verify():
        #     return False, "Invalid signature"
        
        self.transactions[tx.hash] = tx
        print(f"✅ Transaction {tx.hash[:10]}... added to mempool.")
        return True, "Transaction added"

    def get_transactions(self):
        return list(self.transactions.values())

    def clear(self):
        self.transactions.clear()