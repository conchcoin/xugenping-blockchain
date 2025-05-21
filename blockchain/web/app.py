from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from ..core.blockchain import Blockchain
from ..wallet.wallet import Wallet
from ..miner.miner import Miner
from ..api.contract_api import contract_api

app = Flask(__name__)
CORS(app)

# Global variables
blockchain = None
wallet = None
miner = None

# Register blueprints
app.register_blueprint(contract_api, url_prefix='/api/contracts')

def load_blockchain():
    global blockchain, wallet, miner
    try:
        with open('blockchain.json', 'r') as f:
            blockchain_data = json.load(f)
        with open('wallet.json', 'r') as f:
            wallet_data = json.load(f)
        
        blockchain = Blockchain()
        blockchain.chain = blockchain_data['chain']
        wallet = Wallet.from_dict(wallet_data)
        miner = Miner(blockchain, wallet)
    except FileNotFoundError:
        blockchain = Blockchain()
        wallet = Wallet()
        miner = Miner(blockchain, wallet)

@app.route('/api/blockchain', methods=['GET'])
def get_blockchain():
    if blockchain is None:
        load_blockchain()
    return jsonify(blockchain.to_dict())

@app.route('/api/wallet', methods=['GET'])
def get_wallet():
    if wallet is None:
        load_blockchain()
    return jsonify(wallet.to_dict())

@app.route('/api/balance', methods=['GET'])
def get_balance():
    if blockchain is None or wallet is None:
        load_blockchain()
    balance = blockchain.get_balance(wallet.address)
    return jsonify({'balance': balance})

@app.route('/api/transaction', methods=['POST'])
def create_transaction():
    if blockchain is None or wallet is None:
        load_blockchain()
    
    data = request.get_json()
    recipient = data.get('recipient')
    amount = float(data.get('amount'))
    
    if not recipient or not amount:
        return jsonify({'error': 'Missing recipient or amount'}), 400
    
    # Create and sign transaction
    transaction = {
        'from': wallet.address,
        'to': recipient,
        'amount': amount
    }
    signature = wallet.sign_transaction(transaction)
    transaction['signature'] = signature
    
    # Add transaction to blockchain
    blockchain.add_transaction(wallet.address, recipient, amount)
    
    # Save updated blockchain
    with open('blockchain.json', 'w') as f:
        json.dump(blockchain.to_dict(), f, indent=4)
    
    return jsonify({'message': 'Transaction created', 'transaction': transaction})

@app.route('/api/mine', methods=['POST'])
def start_mining():
    if miner is None:
        load_blockchain()
    
    if not miner.is_mining:
        miner.start_mining()
        return jsonify({'message': 'Mining started'})
    return jsonify({'message': 'Mining already in progress'})

@app.route('/api/mine/stop', methods=['POST'])
def stop_mining():
    if miner is None:
        load_blockchain()
    
    if miner.is_mining:
        miner.stop_mining()
        return jsonify({'message': 'Mining stopped'})
    return jsonify({'message': 'Mining not in progress'})

@app.route('/api/mine/status', methods=['GET'])
def mining_status():
    if miner is None:
        load_blockchain()
    return jsonify(miner.get_mining_status())

@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy'}

if __name__ == '__main__':
    load_blockchain()
    app.run(host='0.0.0.0', port=5000) 