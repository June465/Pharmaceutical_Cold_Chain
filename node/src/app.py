# node/src/app.py
import os
from flask import Flask, jsonify, g
from .node import Node
from .api.wallet import wallet_bp, crypto_bp
from .api.transaction import tx_bp
from .api.gossip import gossip_bp
from .api.blockchain import blockchain_bp, debug_bp
from .api.contract import contract_bp

def create_app():
    app = Flask(__name__)
    app.config['NODE_ID'] = os.environ.get('NODE_ID', 'node-unknown')
    app.node_instance = Node(node_id=app.config['NODE_ID'])

    @app.before_request
    def before_request_func():
        g.node = app.node_instance

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'ok': True, 'nodeId': app.config['NODE_ID']}), 200

    app.register_blueprint(wallet_bp, url_prefix='/wallet')
    app.register_blueprint(crypto_bp, url_prefix='/crypto')
    app.register_blueprint(tx_bp, url_prefix='/tx')
    app.register_blueprint(gossip_bp, url_prefix='/gossip')
    app.register_blueprint(blockchain_bp, url_prefix='/chain')
    app.register_blueprint(debug_bp, url_prefix='/debug')
    app.register_blueprint(contract_bp, url_prefix='/contract')
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)