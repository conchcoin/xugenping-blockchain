from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import base64
import json

class Wallet:
    def __init__(self):
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.publickey()
        self.address = self.generate_address()

    def generate_address(self) -> str:
        # Generate a simple address from the public key
        public_key_bytes = self.public_key.export_key()
        return base64.b64encode(public_key_bytes).decode('utf-8')

    def sign_transaction(self, transaction: dict) -> str:
        # Create a copy of the transaction without the signature
        transaction_copy = transaction.copy()
        if 'signature' in transaction_copy:
            del transaction_copy['signature']

        # Create a hash of the transaction
        transaction_hash = SHA256.new(json.dumps(transaction_copy, sort_keys=True).encode())

        # Sign the hash
        signer = PKCS1_v1_5.new(self.private_key)
        signature = signer.sign(transaction_hash)

        # Return the signature as a base64 string
        return base64.b64encode(signature).decode('utf-8')

    def verify_transaction(self, transaction: dict, signature: str, public_key: str) -> bool:
        # Create a copy of the transaction without the signature
        transaction_copy = transaction.copy()
        if 'signature' in transaction_copy:
            del transaction_copy['signature']

        # Create a hash of the transaction
        transaction_hash = SHA256.new(json.dumps(transaction_copy, sort_keys=True).encode())

        # Import the public key
        public_key_obj = RSA.import_key(base64.b64decode(public_key))

        # Verify the signature
        verifier = PKCS1_v1_5.new(public_key_obj)
        return verifier.verify(transaction_hash, base64.b64decode(signature))

    def to_dict(self) -> dict:
        return {
            'address': self.address,
            'public_key': self.public_key.export_key().decode('utf-8'),
            'private_key': self.private_key.export_key().decode('utf-8')
        }

    @classmethod
    def from_dict(cls, wallet_dict: dict) -> 'Wallet':
        wallet = cls()
        wallet.private_key = RSA.import_key(wallet_dict['private_key'].encode())
        wallet.public_key = RSA.import_key(wallet_dict['public_key'].encode())
        wallet.address = wallet_dict['address']
        return wallet 