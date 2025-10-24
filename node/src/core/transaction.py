# node/src/core/transaction.py
import time
import rlp
from ..crypto.wallet import Wallet, hash_data, sign_data, verify_signature

class Transaction:
    def __init__(self, sender, to, amount, nonce, data="", timestamp=None, signature=None, tx_hash=None):
        self.nonce = nonce
        self.sender = sender
        self.to = to
        self.amount = amount
        self.data = data
        self.timestamp = timestamp or int(time.time())
        self.signature = signature
        self.hash = tx_hash

    def to_dict(self):
        return {"nonce": self.nonce, "from": self.sender, "to": self.to, "amount": self.amount, "data": self.data,
                "timestamp": self.timestamp, "signature": self.signature, "hash": self.hash}

    @classmethod
    def from_dict(cls, data):
        return cls(sender=data['from'], to=data['to'], amount=data['amount'], nonce=data['nonce'], data=data.get('data'),
                   timestamp=data['timestamp'], signature=data['signature'], tx_hash=data.get('hash'))

    def _get_signing_payload(self):
        return rlp.encode([self.nonce, self.sender.encode('utf-8'), self.to.encode('utf-8'),
                           self.amount, self.data.encode('utf-8'), self.timestamp])

    def sign(self, wallet: Wallet):
        signing_hash = hash_data(self._get_signing_payload().hex())
        self.signature = sign_data(wallet, signing_hash)
        self.hash = self.compute_hash()

    def compute_hash(self):
        full_tx_list = [self.nonce, self.sender.encode('utf-8'), self.to.encode('utf-8'), self.amount,
                        self.data.encode('utf-8'), self.timestamp, str(self.signature).encode('utf-8')]
        return hash_data(rlp.encode(full_tx_list).hex()).hex()