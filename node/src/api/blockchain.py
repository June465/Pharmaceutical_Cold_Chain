# node/src/api/blockchain.py
from flask import Blueprint, jsonify, current_app

# No longer need to import Block or the separate mempool
# from ..core.block import Block
# from .transaction import mempool 

blockchain_bp = Blueprint('blockchain', __name__)
debug_bp = Blueprint('debug', __name__)

# REMOVED: The global blockchain_instance and get_blockchain() function are obsolete.
# The correct instance is on current_app.blockchain, attached in app.py.

@blockchain_bp.route('/block/height/<int:height>/', methods=['GET'])
def get_block_by_height(height):
    # Use the central blockchain instance from the app context
    blockchain = current_app.blockchain
    block = blockchain.get_block_by_height(height)
    if block:
        return jsonify(block.to_dict())
    return jsonify({'error': 'Block not found'}), 404

@blockchain_bp.route('/block/<string:hash>/', methods=['GET'])
def get_block_by_hash(hash):
    # Use the central blockchain instance
    blockchain = current_app.blockchain
    block = blockchain.get_block_by_hash(hash)
    if block:
        return jsonify(block.to_dict())
    return jsonify({'error': 'Block not found'}), 404
    
@debug_bp.route('/mine', methods=['POST'])
def mine_block():
    """
    Triggers the primary node (node1) to start a PBFT consensus round.
    """
    blockchain = current_app.blockchain
    node_id = current_app.config['NODE_ID']

    if node_id != 'node1':
        return jsonify({'error': 'Only the primary node (node1) can initiate mining.'}), 403

    success = blockchain.pbft_node.start_consensus()
    
    if success:
        return jsonify({'message': 'Consensus process initiated by primary node.'}), 202
    else:
        return jsonify({'message': 'Consensus not started (e.g., mempool empty).'}), 200