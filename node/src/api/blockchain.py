# node/src/api/blockchain.py
from flask import Blueprint, jsonify, current_app
from ..core.blockchain import Blockchain
from ..core.block import Block
from .transaction import mempool # Import our global mempool

blockchain_bp = Blueprint('blockchain', __name__)
debug_bp = Blueprint('debug', __name__)

# This is a shortcut. The blockchain instance is created when the first request comes in.
# A better approach uses the Flask application factory pattern more robustly.
blockchain_instance = None

def get_blockchain():
    global blockchain_instance
    if blockchain_instance is None:
        node_id = current_app.config['NODE_ID']
        blockchain_instance = Blockchain(node_id=node_id)
    return blockchain_instance

@blockchain_bp.route('/block/height/<int:height>', methods=['GET'])
def get_block_by_height(height):
    blockchain = get_blockchain()
    block = blockchain.get_block_by_height(height)
    if block:
        return jsonify(block.to_dict())
    return jsonify({'error': 'Block not found'}), 404

@blockchain_bp.route('/block/<string:hash>', methods=['GET'])
def get_block_by_hash(hash):
    blockchain = get_blockchain()
    block = blockchain.get_block_by_hash(hash)
    if block:
        return jsonify(block.to_dict())
    return jsonify({'error': 'Block not found'}), 404
    
# --- TEMPORARY DEBUG ENDPOINT ---
@debug_bp.route('/mine', methods=['POST'])
def mine_block():
    """
    A temporary endpoint to manually create a block from mempool transactions.
    In a real consensus mechanism (Phase 5), this would be automated.
    """
    blockchain = get_blockchain()
    node_id = current_app.config['NODE_ID']
    
    last_block = blockchain.get_head()
    txs_to_include = mempool.get_transactions()
    
    new_block = Block(
        index=last_block.header['index'] + 1,
        prev_hash=last_block.hash,
        proposer_id=node_id,
        transactions=txs_to_include
    )
    
    blockchain.add_block(new_block)
    
    # Clear the mempool after including transactions in a block
    mempool.clear()
    
    # TODO: In Phase 5, we will broadcast this new block to peers.
    
    return jsonify({'message': 'New block forged', 'block': new_block.to_dict()}), 201