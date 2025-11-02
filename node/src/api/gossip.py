# node/src/api/gossip.py
from flask import Blueprint, request, jsonify, current_app

gossip_bp = Blueprint('gossip', __name__)

@gossip_bp.route('/tx', methods=['POST'])
def receive_gossip_tx():
    tx_data = request.get_json()
    blockchain = current_app.blockchain
    mempool = blockchain.mempool
    
    # Basic validation before adding to mempool
    if tx_data and 'hash' in tx_data:
        if not mempool.is_in_mempool(tx_data['hash']):
            print(f"Received gossiped transaction: {tx_data['hash'][:10]}...")
            mempool.add_transaction_from_dict(tx_data)
        return jsonify({'message': 'Transaction received'}), 200
    
    return jsonify({'error': 'Invalid transaction data'}), 400

# --- ADD THIS NEW ENDPOINT ---
@gossip_bp.route('/consensus', methods=['POST'])
def receive_consensus_message():
    """Receives consensus messages (PRE-PREPARE, PREPARE, COMMIT)."""
    message = request.get_json()
    blockchain = current_app.blockchain
    
    if not message or 'type' not in message:
        return jsonify({'error': 'Invalid consensus message'}), 400

    blockchain.pbft_node.handle_consensus_message(message)
    
    return jsonify({'status': 'ok'}), 200