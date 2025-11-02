# node/src/api/system.py
from flask import Blueprint, jsonify, current_app

system_bp = Blueprint('system', __name__)

@system_bp.route('/contract/', methods=['GET'])
def get_system_contract_address():
    """Returns the address of the core PharmaContract."""
    address = current_app.blockchain.pharma_contract_address
    if address:
        return jsonify({'contract_address': address}), 200
    else:
        return jsonify({'error': 'Contract address not available yet.'}), 404