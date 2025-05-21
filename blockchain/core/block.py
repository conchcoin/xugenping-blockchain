import hashlib
import json
import time
from typing import List, Dict, Any
from ..config.token import TOKEN_SYMBOL, get_block_reward

class Block:
    def __init__(self, index: int, transactions: List[Dict[str, Any]], timestamp: float,
                 previous_hash: str, nonce: int = 0, miner_address: str = None):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.miner_address = miner_address
        self.reward = get_block_reward(index)
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate the hash of the block"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'miner_address': self.miner_address,
            'reward': self.reward
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash,
            'hash': self.hash,
            'nonce': self.nonce,
            'miner_address': self.miner_address,
            'reward': self.reward,
            'reward_symbol': TOKEN_SYMBOL
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        """Create block from dictionary"""
        block = cls(
            index=data['index'],
            transactions=data['transactions'],
            timestamp=data['timestamp'],
            previous_hash=data['previous_hash'],
            nonce=data['nonce'],
            miner_address=data['miner_address']
        )
        block.hash = data['hash']
        return block

    def __str__(self) -> str:
        return f"Block #{self.index} - Reward: {self.reward} {TOKEN_SYMBOL}" 