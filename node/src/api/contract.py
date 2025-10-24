# node/src/api/contract.py
import json
from flask import Blueprint, jsonify, request, g
from ..core.transaction import Transaction
from ..p2p.gossip import broadcast_transaction
from .transaction import mempool

contract_bp = Blueprint('contract', __name__)

@contract_bp.route('/deploy', methods=['POST'])
def deploy_contract():
    data = request.get_json()
    required = ['from', 'nonce', 'contract', 'args']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    tx_data_payload = json.dumps({'contract': data['contract'], 'args': data['args']})
    tx = Transaction(sender=data['from'], to="0x0", amount=0, nonce=data['nonce'], data=tx_data_payload)
    tx.signature = "placeholder_signature"
    tx.hash = tx.compute_hash()
    
    success, msg = mempool.add_transaction(tx)
    if success:
        broadcast_transaction(tx)
        return jsonify({'message': 'Contract deployment transaction submitted', 'txHash': tx.hash}), 202
    return jsonify({'error': msg}), 400

@contract_bp.route('/call', methods=['POST'])
def call_contract():
    data = request.get_json()
    required = ['from', 'nonce', 'to', 'method', 'args']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    tx_data_payload = json.dumps({'method': data['method'], 'args': data['args']})
    tx = Transaction(sender=data['from'], to=data['to'], amount=0, nonce=data['nonce'], data=tx_data_payload)
    tx.signature = "placeholder_signature"
    tx.hash = tx.compute_hash()

    success, msg = mempool.add_transaction(tx)
    if success:
        broadcast_transaction(tx)
        return jsonify({'message': 'Contract call transaction submitted', 'txHash': tx.hash}), 202
    return jsonify({'error': msg}), 400

@contract_bp.route('/state/<string:address>/<string:key>', methods=['GET'])
def get_state(address, key):
    storage = g.node.blockchain.world_state.get_account_storage(address)
    if storage:
        value = storage.get(key)
        return jsonify({'address': address, 'key': key, 'value': value})
    return jsonify({'error': 'Address not found or no state available'}), 404