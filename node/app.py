# node/app.py
import os
import sys
from flask import Flask, jsonify

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# --- Other imports ---
from src.core.blockchain import Blockchain # <-- ADD THIS IMPORT
from src.api.system import system_bp # <-- IMPORT
from src.api.wallet import wallet_bp, crypto_bp
from src.api.transaction import tx_bp
from src.api.gossip import gossip_bp
from src.api.blockchain import blockchain_bp, debug_bp
from src.api.contract import contract_bp # <-- 1. IMPORT THE NEW BLUEPRINT

def create_app():
    """Application factory function"""
    app = Flask(__name__)

    app.config['NODE_ID'] = os.environ.get('NODE_ID', 'node-unknown')

    # --- This is the corrected section ---
    # Get the node_id from the application config
    node_id = app.config['NODE_ID']
    # Pass the node_id when creating the Blockchain instance
    app.blockchain = Blockchain(node_id=node_id)
    # ------------------------------------
    
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
    app.register_blueprint(contract_bp, url_prefix='/contract')
    app.register_blueprint(system_bp, url_prefix='/system')

    return app

if __name__ == '__main__':
    app = create_app()
    # The FLASK_RUN_PORT env var is used in docker-compose, let's respect it
    port = int(os.environ.get('FLASK_RUN_PORT', 8000))
    app.run(host='0.0.0.0', port=port)