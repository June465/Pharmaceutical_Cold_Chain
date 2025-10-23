# node/src/api/wallet.py
from flask import Blueprint, jsonify, request
from src.crypto.wallet import Wallet, hash_data, verify_signature

# A Blueprint is a way to organize a group of related views and other code.
wallet_bp = Blueprint('wallet', __name__)
crypto_bp = Blueprint('crypto', __name__)

# --- Wallet Endpoints ---

@wallet_bp.route('/new', methods=['POST'])
def new_wallet():
    """
    Creates a new wallet and returns its details.
    """
    wallet = Wallet()
    return jsonify({
        'privateKey': wallet.private_key,
        'publicKey': wallet.public_key,
        'address': wallet.address
    }), 201

# In a real system, we'd add encryption with a user-provided password.
# For now, we'll keep it simple and just restore from a private key.
@wallet_bp.route('/restore', methods=['POST'])
def restore_wallet():
    """
    Restores a wallet from a given private key.
    """
    data = request.get_json()
    if not data or 'privateKey' not in data:
        return jsonify({'error': 'Private key is required'}), 400
    
    try:
        private_key_bytes = bytes.fromhex(data['privateKey'])
        wallet = Wallet(private_key_bytes=private_key_bytes)
        return jsonify({
            'privateKey': wallet.private_key,
            'publicKey': wallet.public_key,
            'address': wallet.address
        }), 200
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid private key format'}), 400


# --- Crypto Endpoints ---

@crypto_bp.route('/verify', methods=['POST'])
def verify_message():
    """
    Verifies if a signature is valid for a given message and public key.
    """
    data = request.get_json()
    required_fields = ['publicKey', 'signature', 'message']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields: publicKey, signature, message'}), 400
    
    # 1. Hash the original message
    data_hash = hash_data(data['message'])

    # 2. Verify the signature
    is_valid = verify_signature(
        public_key_hex=data['publicKey'],
        signature_hex=data['signature'],
        data_hash=data_hash
    )

    return jsonify({
        'isValid': is_valid
    })