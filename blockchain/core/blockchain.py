import json
import time
from typing import List, Dict, Any
from .block import Block

class Blockchain:
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = [self.create_genesis_block()]
        self.difficulty = difficulty
        self.pending_transactions: List[Dict[str, Any]] = []
        self.mining_reward = 10

    def create_genesis_block(self) -> Block:
        return Block(0, [], time.time(), "0" * 64)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def mine_pending_transactions(self, miner_address: str) -> None:
        # Create mining reward transaction
        reward_tx = {
            "from": "network",
            "to": miner_address,
            "amount": self.mining_reward
        }
        self.pending_transactions.append(reward_tx)

        # Create new block with pending transactions
        block = Block(
            len(self.chain),
            self.pending_transactions,
            time.time(),
            self.get_latest_block().hash
        )

        # Mine the block
        block.mine_block(self.difficulty)

        # Add the block to the chain
        self.chain.append(block)

        # Reset pending transactions
        self.pending_transactions = []

    def add_transaction(self, sender: str, recipient: str, amount: float) -> None:
        self.pending_transactions.append({
            "from": sender,
            "to": recipient,
            "amount": amount
        })

    def get_balance(self, address: str) -> float:
        balance = 0

        for block in self.chain:
            for transaction in block.transactions:
                if transaction["from"] == address:
                    balance -= transaction["amount"]
                if transaction["to"] == address:
                    balance += transaction["amount"]

        return balance

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Verify current block's hash
            if current_block.hash != current_block.calculate_hash():
                return False

            # Verify chain linkage
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain": [block.to_dict() for block in self.chain],
            "difficulty": self.difficulty,
            "pending_transactions": self.pending_transactions
        } 