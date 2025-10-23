# node/src/api/gossip.py
from flask import Blueprint, jsonify, request
from src.core.transaction import Transaction

from .transaction import mempool

gossip_bp = Blueprint('gossip', __name__)

@gossip_bp.route('/tx', methods=['POST'])
def receive_gossiped_tx():
    """
    An endpoint specifically for receiving transactions from other peers.
    It validates and adds the transaction to the mempool but does NOT
    broadcast it again. This prevents network storms.
    """
    data = request.get_json()
    required_fields = ['from', 'to', 'amount', 'nonce', 'signature']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required transaction fields'}), 400

    try:
        tx = Transaction(
            sender=data['from'],
            to=data['to'],
            amount=int(data['amount']),
            nonce=int(data['nonce']),
            data=data.get('data', ""),
            timestamp=int(data['timestamp']),
            signature=data['signature']
        )
        tx.hash = tx.compute_hash()

        # We use the same mempool to add the transaction
        success, message = mempool.add_transaction(tx)
        
        if success:
            print(f" Gossiped tx {tx.hash[:10]}... accepted.")
            return jsonify({'message': 'Transaction accepted'}), 202
        else:
            # It's common to receive a duplicate, which is not an error.
            # The mempool handles this gracefully.
            print(f" Gossiped tx rejected: {message}")
            return jsonify({'message': message}), 208 # 208 Already Reported
    except Exception as e:
        print(f"Error processing gossiped tx: {e}")
        return jsonify({'error': 'Invalid transaction data'}), 400