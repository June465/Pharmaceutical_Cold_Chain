# node/src/api/transaction.py
from flask import Blueprint, jsonify, request
from src.core.transaction import Transaction
from src.core.mempool import Mempool
from src.p2p.gossip import broadcast_transaction

# Let's create a single, global mempool instance for our node
# In a more advanced app, this would be managed by a central Node class.
mempool = Mempool()

tx_bp = Blueprint('transaction', __name__)

@tx_bp.route('/', methods=['POST'])
def create_transaction():
    """
    Receives a new transaction, validates it, and adds it to the mempool.
    The transaction is expected to be already signed.
    """
    data = request.get_json()
    required_fields = ['from', 'to', 'amount', 'nonce', 'signature']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required transaction fields'}), 400

    # Reconstruct the Transaction object from the request data
    tx = Transaction(
        sender=data['from'],
        to=data['to'],
        amount=int(data['amount']),
        nonce=int(data['nonce']),
        data=data.get('data', ""),
        timestamp=int(data['timestamp']),
        signature=data['signature']
    )
    
    # Before adding, compute its hash to ensure consistency
    tx.hash = tx.compute_hash()

    # Add to our node's mempool
    success, message = mempool.add_transaction(tx)
    
    if success:
        # TODO: In Phase 3, we will broadcast this transaction to peers.
        return jsonify({'message': message, 'txHash': tx.hash}), 202 # 202 Accepted
    else:
        print(f"❌ Transaction rejected: {message}")
        return jsonify({'error': message}), 400 # 400 Bad Request

@tx_bp.route('/mempool', methods=['GET'])
def get_mempool():
    """
    Returns the list of all transactions currently in the mempool.
    """
    transactions_in_pool = [tx.to_dict() for tx in mempool.get_transactions()]
    return jsonify({
        'transactions': transactions_in_pool,
        'count': len(transactions_in_pool)
    })