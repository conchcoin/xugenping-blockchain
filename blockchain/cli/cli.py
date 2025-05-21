import click
import json
from ..core.blockchain import Blockchain
from ..wallet.wallet import Wallet
from ..miner.miner import Miner

@click.group()
def cli():
    """Blockchain CLI tool"""
    pass

@cli.command()
@click.option('--difficulty', default=4, help='Mining difficulty')
def init(difficulty):
    """Initialize a new blockchain"""
    blockchain = Blockchain(difficulty)
    wallet = Wallet()
    
    # Save blockchain and wallet data
    with open('blockchain.json', 'w') as f:
        json.dump(blockchain.to_dict(), f, indent=4)
    
    with open('wallet.json', 'w') as f:
        json.dump(wallet.to_dict(), f, indent=4)
    
    click.echo(f"Blockchain initialized with difficulty {difficulty}")
    click.echo(f"Wallet address: {wallet.address}")

@cli.command()
def balance():
    """Check wallet balance"""
    try:
        with open('blockchain.json', 'r') as f:
            blockchain_data = json.load(f)
        with open('wallet.json', 'r') as f:
            wallet_data = json.load(f)
        
        blockchain = Blockchain()
        blockchain.chain = blockchain_data['chain']
        balance = blockchain.get_balance(wallet_data['address'])
        click.echo(f"Balance: {balance}")
    except FileNotFoundError:
        click.echo("Blockchain not initialized. Run 'init' first.")

@cli.command()
@click.argument('recipient')
@click.argument('amount', type=float)
def send(recipient, amount):
    """Send coins to another address"""
    try:
        with open('blockchain.json', 'r') as f:
            blockchain_data = json.load(f)
        with open('wallet.json', 'r') as f:
            wallet_data = json.load(f)
        
        blockchain = Blockchain()
        blockchain.chain = blockchain_data['chain']
        wallet = Wallet.from_dict(wallet_data)
        
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
        
        click.echo(f"Transaction sent: {amount} to {recipient}")
    except FileNotFoundError:
        click.echo("Blockchain not initialized. Run 'init' first.")

@cli.command()
def mine():
    """Start mining"""
    try:
        with open('blockchain.json', 'r') as f:
            blockchain_data = json.load(f)
        with open('wallet.json', 'r') as f:
            wallet_data = json.load(f)
        
        blockchain = Blockchain()
        blockchain.chain = blockchain_data['chain']
        wallet = Wallet.from_dict(wallet_data)
        
        miner = Miner(blockchain, wallet)
        click.echo("Starting mining...")
        miner.start_mining()
    except FileNotFoundError:
        click.echo("Blockchain not initialized. Run 'init' first.")

if __name__ == '__main__':
    cli() 