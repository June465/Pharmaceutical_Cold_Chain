# node/app.py
import os
import sys
from flask import Flask, jsonify

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.api.wallet import wallet_bp, crypto_bp
from src.api.transaction import tx_bp
from src.api.gossip import gossip_bp
from src.api.blockchain import blockchain_bp, debug_bp

def create_app():
    """Application factory function"""
    app = Flask(__name__)

    app.config['NODE_ID'] = os.environ.get('NODE_ID', 'node-unknown')
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'ok': True,
            'nodeId': app.config['NODE_ID']
        }), 200

    # Register our blueprints
    app.register_blueprint(wallet_bp, url_prefix='/wallet')
    app.register_blueprint(crypto_bp, url_prefix='/crypto')
    app.register_blueprint(tx_bp, url_prefix='/tx')
    app.register_blueprint(gossip_bp, url_prefix='/gossip')
    app.register_blueprint(blockchain_bp, url_prefix='/chain') 
    app.register_blueprint(debug_bp, url_prefix='/debug')

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)