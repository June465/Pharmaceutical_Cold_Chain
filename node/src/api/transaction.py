# node/src/api/transaction.py
from flask import Blueprint, jsonify, request, current_app
from src.p2p.gossip import broadcast_transaction
from src.utils.logger import get_logger

log = get_logger(__name__)
tx_bp = Blueprint('transaction', __name__)

@tx_bp.route('/', methods=['POST'])
def create_transaction():
    mempool = current_app.blockchain.mempool
    data = request.get_json()
    if not data: return jsonify({'error': 'Invalid request body'}), 400

    success, message_or_tx_hash = mempool.add_transaction_from_dict(data)
    
    if success:
        tx_hash = message_or_tx_hash
        tx = mempool.get_transaction_by_hash(tx_hash)
        if tx: broadcast_transaction(tx)
        return jsonify({'message': 'Transaction added to mempool', 'txHash': tx_hash}), 202
    else:
        error_message = message_or_tx_hash
        log.warning(f"Transaction rejected: {error_message}")
        return jsonify({'error': error_message}), 400

@tx_bp.route('/mempool/', methods=['GET'])
def get_mempool():
    mempool = current_app.blockchain.mempool
    transactions = [tx.to_dict() for tx in mempool.get_transactions()]
    return jsonify({'transactions': transactions, 'count': len(transactions)})