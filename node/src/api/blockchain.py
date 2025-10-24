# node/src/api/blockchain.py
from flask import Blueprint, jsonify, g, request
from .transaction import mempool
from ..core.block import Block
from ..vm.executor import generate_contract_address

blockchain_bp = Blueprint('blockchain', __name__)
debug_bp = Blueprint('debug', __name__)

@blockchain_bp.route('/block/height/<int:height>', methods=['GET'])
def get_block_by_height(height):
    block = g.node.blockchain.get_block_by_height(height)
    if block:
        return jsonify(block.to_dict())
    return jsonify({'error': 'Block not found'}), 404

@debug_bp.route('/mine', methods=['POST'])
def mine_block():
    node = g.node
    if not node.pbft_node.is_primary():
        return jsonify({'error': f"Only the primary node ({node.pbft_node.primary}) can start mining."}), 403

    last_block = node.blockchain.get_head()
    txs_to_include = mempool.get_transactions()

    new_block = Block(
        index=last_block.header['index'] + 1,
        prev_hash=last_block.hash,
        proposer_id=node.pbft_node.node_id,
        transactions=txs_to_include
    )
    node.pbft_node.start_consensus(new_block)
    mempool.clear()
    return jsonify({'message': 'Consensus process started for new block'}), 202

@debug_bp.route('/contract-address', methods=['POST'])
def get_contract_address():
    data = request.get_json()
    if not data or 'sender' not in data or 'nonce' not in data:
        return jsonify({'error': 'Missing sender or nonce'}), 400
    address = generate_contract_address(data['sender'], int(data['nonce']))
    return jsonify({'contractAddress': address})