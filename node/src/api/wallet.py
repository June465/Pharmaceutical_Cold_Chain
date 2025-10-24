# node/src/api/wallet.py
from flask import Blueprint, jsonify, request
from ..crypto.wallet import Wallet, hash_data, verify_signature

wallet_bp = Blueprint('wallet', __name__)
crypto_bp = Blueprint('crypto', __name__)

@wallet_bp.route('/new', methods=['POST'])
def new_wallet():
    wallet = Wallet()
    return jsonify({'privateKey': wallet.private_key, 'publicKey': wallet.public_key, 'address': wallet.address}), 201

@crypto_bp.route('/verify', methods=['POST'])
def verify_message():
    data = request.get_json()
    required_fields = ['publicKey', 'signature', 'message']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: publicKey, signature, message'}), 400
    
    data_hash = hash_data(data['message'])
    is_valid = verify_signature(public_key_hex=data['publicKey'], signature_hex=data['signature'], data_hash=data_hash)
    return jsonify({'isValid': is_valid})