# node/src/api/contract.py
from flask import Blueprint, request, jsonify, current_app

contract_bp = Blueprint('contract', __name__)

@contract_bp.route('/deploy/', methods=['POST'])
def deploy_contract():
    data = request.get_json()
    if not data or 'contract_name' not in data:
        return jsonify({'error': 'Missing contract_name in request body'}), 400

    from ..core.transaction import Transaction
    deployment_tx = Transaction(
        sender=data.get('from', '0x_genesis_deployer'),
        to='0x0',
        amount=0,
        nonce=0, # Nonce can be 0 for this special tx
        data=data['contract_name']
    )
    deployment_tx.signature = "unsigned_deployment_tx"
    deployment_tx.hash = deployment_tx.compute_hash()

    blockchain = current_app.blockchain
    mempool = blockchain.mempool
    new_address = blockchain.world_state.create_contract_address(deployment_tx)

    # --- THIS IS THE CRITICAL FIX ---
    # Call the new method for unsigned transactions and check the result.
    success, message = mempool.add_unsigned_tx(deployment_tx)
    
    if not success:
        print(f"❌ Contract deployment rejected by mempool: {message}")
        return jsonify({'error': message}), 400 # Return an error!

    print(f"✅ Contract deployment tx for '{data['contract_name']}' added to mempool. Address will be {new_address}")

    return jsonify({
        'message': f"Contract deployment for {data['contract_name']} submitted to mempool.",
        'transaction_hash': deployment_tx.hash,
        'predicted_address': new_address
    }), 202

@contract_bp.route('/state/<string:address>/', methods=['GET'])
def get_contract_state(address):
    import json
    blockchain = current_app.blockchain
    storage = blockchain.world_state.get_contract_storage(address)

    if storage is None:
        return jsonify({'error': 'Contract not found at the specified address'}), 404
    
    return jsonify(json.loads(storage)), 200