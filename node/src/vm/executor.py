# node/src/vm/executor.py
import json
from importlib import import_module
from src.core.transaction import Transaction
from src.state.world_state import WorldState
from src.utils.logger import get_logger

log = get_logger(__name__)

def execute_transaction(tx: Transaction, world_state: WorldState):
    log.info(f"Executing transaction {tx.hash[:10]}...")
    if tx.to == '0x0':
        _deploy_contract(tx, world_state)
    else:
        _call_contract(tx, world_state)

def _deploy_contract(tx: Transaction, world_state: WorldState):
    contract_name = tx.data
    
    try:
        # --- THIS IS THE FINAL FIX ---
        # Instead of a fragile dynamic name, we explicitly map the contract name
        # to its module. This is much more robust.
        if contract_name == "PharmaContract":
            module_path = "src.contracts.pharma"
        else:
            raise ImportError(f"Unknown contract name: {contract_name}")

        contracts_module = import_module(module_path)
        contract_class = getattr(contracts_module, contract_name)
        # --- END OF FIX ---

    except (ImportError, AttributeError) as e:
        log.error(f"Failed to load contract '{contract_name}': {e}")
        raise Exception(f"Contract '{contract_name}' not found or has an error.")

    new_contract_address = world_state.create_contract_address(tx)
    contract_instance = contract_class()
    
    world_state.set_contract_code(new_contract_address, contract_name)
    world_state.set_contract_storage(new_contract_address, contract_instance.storage)
    log.info(f"✅ Deployed contract '{contract_name}' to address: {new_contract_address}")

def _call_contract(tx: Transaction, world_state: WorldState):
    contract_address = tx.to
    contract_name = world_state.get_contract_code(contract_address)
    storage_json = world_state.get_contract_storage(contract_address)
    if not contract_name or storage_json is None:
        raise Exception(f"Contract not found at address {contract_address}")

    current_storage = json.loads(storage_json)

    try:
        # Also apply the explicit mapping here for consistency
        if contract_name == "PharmaContract":
            module_path = "src.contracts.pharma"
        else:
            raise ImportError(f"Unknown contract name: {contract_name}")

        contracts_module = import_module(module_path)
        contract_class = getattr(contracts_module, contract_name)
        contract_instance = contract_class()
        contract_instance.storage = current_storage
    except (ImportError, AttributeError):
        raise Exception(f"Could not load code for contract '{contract_name}'")

    try:
        call_data = json.loads(tx.data)
        method_name, params = call_data['method'], call_data['params']
    except (json.JSONDecodeError, KeyError):
        raise Exception("Invalid transaction data format for contract call.")

    method_to_call = getattr(contract_instance, method_name, None)
    if not callable(method_to_call):
        raise Exception(f"Method '{method_name}' does not exist on '{contract_name}'")

    log.info(f"-> Calling method '{method_name}' on contract {contract_address}")
    method_to_call(**params)

    updated_storage = contract_instance.storage
    world_state.set_contract_storage(contract_address, updated_storage)
    log.info(f"✅ Successfully updated state for contract {contract_address}")