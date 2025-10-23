# node/src/core/transaction.py
import time
import rlp
from typing import Optional
from src.crypto.wallet import Wallet, hash_data, sign_data, verify_signature

class Transaction:
    """
    Represents a transaction in the blockchain.
    """
    def __init__(self,
                 sender: str,
                 to: str,
                 amount: int,
                 nonce: int,
                 data: Optional[str] = "",
                 timestamp: Optional[int] = None,
                 signature: Optional[str] = None,
                 tx_hash: Optional[str] = None):
        self.nonce = nonce
        self.sender = sender # This will be the public key, not the address
        self.to = to
        self.amount = amount
        self.data = data
        self.timestamp = timestamp or int(time.time())
        self.signature = signature
        self.hash = tx_hash

    def to_dict(self) -> dict:
        """Converts the transaction object to a dictionary."""
        return {
            "nonce": self.nonce,
            "from": self.sender,
            "to": self.to,
            "amount": self.amount,
            "data": self.data,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "hash": self.hash
        }

    def _get_signing_payload(self) -> bytes:
        """
        Creates the canonical payload for signing, using RLP encoding.
        The signature and hash are excluded from this payload.
        """
        # Order is critical for deterministic hashing!
        tx_data_list = [
            self.nonce,
            self.sender.encode('utf-8'),
            self.to.encode('utf-8'),
            self.amount,
            self.data.encode('utf-8'),
            self.timestamp
        ]
        return rlp.encode(tx_data_list)

    def sign(self, wallet: Wallet):
        """Signs the transaction with the provided wallet."""
        if wallet.public_key != self.sender:
            raise ValueError("Wallet's public key does not match transaction sender.")
        
        signing_payload = self._get_signing_payload()
        signing_hash = hash_data(signing_payload.hex()) # Hash the RLP-encoded data
        self.signature = sign_data(wallet, signing_hash)
        
        # After signing, we can generate the final transaction hash
        self.hash = self.compute_hash()

    def verify(self) -> bool:
        """Verifies the transaction's signature."""
        if not self.signature or not self.sender:
            return False
            
        signing_payload = self._get_signing_payload()
        signing_hash = hash_data(signing_payload.hex())

        return verify_signature(
            public_key_hex=self.sender,
            signature_hex=self.signature,
            data_hash=signing_hash
        )

    def compute_hash(self) -> str:
        """
        Computes the final hash of the transaction, including the signature.
        This hash uniquely identifies the transaction.
        """
        # Use RLP encoding on the full transaction data for the final hash
        full_tx_list = [
            self.nonce,
            self.sender.encode('utf-8'),
            self.to.encode('utf-8'),
            self.amount,
            self.data.encode('utf-8'),
            self.timestamp,
            self.signature.encode('utf-8')
        ]
        encoded_tx = rlp.encode(full_tx_list)
        tx_hash_bytes = hash_data(encoded_tx.hex())
        return tx_hash_bytes.hex()