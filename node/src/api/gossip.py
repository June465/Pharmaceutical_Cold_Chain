# node/src/api/gossip.py
from flask import Blueprint, jsonify, request, g
from ..core.transaction import Transaction
from .transaction import mempool

gossip_bp = Blueprint('gossip', __name__)

@gossip_bp.route('/tx', methods=['POST'])
def receive_gossiped_tx():
    data = request.get_json()
    try:
        tx = Transaction(sender=data['from'], to=data['to'], amount=int(data['amount']), nonce=int(data['nonce']),
                         data=data.get('data', ""), timestamp=int(data['timestamp']), signature=data['signature'])
        tx.hash = tx.compute_hash()
        success, message = mempool.add_transaction(tx)
        if success:
            return jsonify({'message': 'Transaction accepted'}), 202
        else:
            return jsonify({'message': message}), 208
    except Exception as e:
        return jsonify({'error': f'Invalid transaction data: {e}'}), 400

@gossip_bp.route('/consensus', methods=['POST'])
def receive_consensus_message():
    msg = request.get_json()
    g.node.pbft_node.handle_message(msg)
    return jsonify({"status": "ok"}), 200