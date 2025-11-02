# node/src/core/mempool.py
from typing import List, Dict
from .transaction import Transaction
from src.utils.logger import get_logger

log = get_logger(__name__)

class Mempool:
    def __init__(self):
        self.transactions: Dict[str, Transaction] = {}
    
    def add_transaction(self, tx: Transaction) -> (bool, str):
        if tx.hash in self.transactions: return False, "Duplicate transaction"
        if not tx.verify(): return False, "Invalid signature"
        self.transactions[tx.hash] = tx
        log.info(f"Signed transaction {tx.hash[:10]}... added to mempool.")
        return True, tx.hash # Return the hash on success

    def add_unsigned_tx(self, tx: Transaction) -> (bool, str):
        if tx.hash in self.transactions: return False, "Duplicate transaction"
        self.transactions[tx.hash] = tx
        log.info(f"Unsigned transaction {tx.hash[:10]}... added to mempool.")
        return True, "Transaction added"

    def add_transaction_from_dict(self, tx_data: dict) -> (bool, str):
        from src.core.transaction import Transaction
        tx = Transaction(
            sender=tx_data['from'], to=tx_data['to'], amount=int(tx_data['amount']),
            nonce=int(tx_data['nonce']), data=tx_data.get('data', ""),
            timestamp=int(tx_data['timestamp']), signature=tx_data['signature']
        )
        tx.hash = tx.compute_hash()
        return self.add_transaction(tx)

    def get_transactions(self) -> List[Transaction]: return list(self.transactions.values())
    def get_transaction_by_hash(self, tx_hash: str) -> Transaction: return self.transactions.get(tx_hash)
    def is_in_mempool(self, tx_hash: str) -> bool: return tx_hash in self.transactions
    def remove_transaction(self, tx_hash: str):
        if tx_hash in self.transactions: del self.transactions[tx_hash]
    def clear(self): self.transactions.clear()