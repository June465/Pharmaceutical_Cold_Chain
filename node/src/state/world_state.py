# node/src/state/world_state.py
import json
from ..db.database import Database

class WorldState:
    def __init__(self, db: Database):
        self.db = db
        self.STATE_PREFIX = b'state:'

    def get_account_storage(self, address: str):
        storage_json = self.db.db.get(self.STATE_PREFIX + address.encode('utf-8'))
        return json.loads(storage_json.decode('utf-8')) if storage_json else None

    def set_account_storage(self, address: str, storage):
        self.db.db.put(self.STATE_PREFIX + address.encode('utf-8'), json.dumps(storage).encode('utf-8'))

    def create_account(self, address: str):
        if self.get_account_storage(address) is None:
            self.set_account_storage(address, {})