# node/src/state/world_state.py
import json
from Crypto.Hash import keccak
from src.db.database import Database
from src.core.transaction import Transaction

# Define database key prefixes for better data organization
CONTRACT_STORAGE_PREFIX = b'contract_storage:'
CONTRACT_CODE_PREFIX = b'contract_code:'

class WorldState:
    """
    Manages the global state of all smart contracts.
    It uses the main database for persistent storage.
    """
    def __init__(self, db: Database):
        self.db = db.db  # Use the underlying plyvel DB object
        self.state_root = self._calculate_current_state_root()

    def create_contract_address(self, tx: Transaction) -> str:
        """
        Deterministically creates a new contract address from the sender and nonce.
        This mimics Ethereum's address generation.
        """
        # For our simple, unsigned deployment, we use the tx hash for determinism
        hasher = keccak.new(digest_bits=256)
        hasher.update(tx.hash.encode('utf-8'))
        return '0x' + hasher.digest()[-20:].hex()

    def set_contract_code(self, address: str, contract_name: str):
        """Stores the name of the contract class associated with an address."""
        key = CONTRACT_CODE_PREFIX + address.encode('utf-8')
        self.db.put(key, contract_name.encode('utf-8'))
        print(f"Stored code '{contract_name}' for contract {address}")

    def get_contract_code(self, address: str) -> str or None:
        """Retrieves the contract class name for a given address."""
        key = CONTRACT_CODE_PREFIX + address.encode('utf-8')
        code = self.db.get(key)
        return code.decode('utf-8') if code else None

    def set_contract_storage(self, address: str, storage: dict):
        """Saves the contract's state (as a JSON string) to the database."""
        key = CONTRACT_STORAGE_PREFIX + address.encode('utf-8')
        self.db.put(key, json.dumps(storage).encode('utf-8'))
        self._update_on_change()

    def get_contract_storage(self, address: str) -> str or None:
        """Retrieves the contract's state (as a JSON string) from the database."""
        key = CONTRACT_STORAGE_PREFIX + address.encode('utf-8')
        storage_json = self.db.get(key)
        return storage_json.decode('utf-8') if storage_json else None
    
    def update_state_root(self, block_header: dict):
        """Updates the given block header with the current state root."""
        self.state_root = self._calculate_current_state_root()
        block_header['stateRoot'] = self.state_root

    def _calculate_current_state_root(self) -> str:
        """
        Calculates a hash of the entire contract state.
        A simple implementation: hash all contract storage keys and values.
        """
        hasher = keccak.new(digest_bits=256)
        # Iterate over all contract storage entries
        for key, value in self.db.iterator(prefix=CONTRACT_STORAGE_PREFIX):
            hasher.update(key)
            hasher.update(value)
        return hasher.hexdigest()

    def _update_on_change(self):
        """Recalculates the state root whenever state changes."""
        self.state_root = self._calculate_current_state_root()

    def find_contract_address_by_name(self, contract_name_to_find: str) -> str or None:
        """Iterates through contract code to find the address of a named contract."""
        for key, value in self.db.iterator(prefix=CONTRACT_CODE_PREFIX):
            if value.decode('utf-8') == contract_name_to_find:
                # The address is part of the key, after the prefix
                return key[len(CONTRACT_CODE_PREFIX):].decode('utf-8')
        return None