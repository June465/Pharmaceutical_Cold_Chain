# node/src/vm/executor.py
import json
from ..core.transaction import Transaction
from ..state.world_state import WorldState
from ..contracts.pharma import PharmaContract
from ..crypto.wallet import hash_data

CONTRACT_REGISTRY = {'PharmaContract': PharmaContract}

def generate_contract_address(sender_pub_key: str, nonce: int):
    payload = f"{sender_pub_key}{nonce}".encode('utf-8')
    return '0x' + hash_data(payload.hex()).hex()

def execute_transaction(tx: Transaction, world_state: WorldState):
    try:
        if tx.to == "0x0": # Deploy
            payload = json.loads(tx.data)
            contract_class = CONTRACT_REGISTRY.get(payload['contract'])
            if contract_class:
                contract_address = generate_contract_address(tx.sender, tx.nonce)
                world_state.create_account(contract_address)
                instance = contract_class(contract_address, world_state, tx.sender)
                instance.constructor(*payload['args'])
                instance.save_storage()
                print(f"✅ Deployed '{payload['contract']}' to address {contract_address}")
        elif world_state.get_account_storage(tx.to) is not None: # Call
            payload = json.loads(tx.data)
            instance = PharmaContract(tx.to, world_state, tx.sender) # Simplified for now
            method_to_call = getattr(instance, payload['method'], None)
            if callable(method_to_call):
                method_to_call(*payload['args'])
                instance.save_storage()
                print(f"✅ Called '{payload['method']}' on contract {tx.to}")
    except Exception as e:
        print(f"❌ VM EXECUTION FAILED for tx {tx.hash[:10]}: {e}")