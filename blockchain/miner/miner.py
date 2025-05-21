import time
from typing import Optional
from ..core.blockchain import Blockchain
from ..wallet.wallet import Wallet

class Miner:
    def __init__(self, blockchain: Blockchain, wallet: Wallet):
        self.blockchain = blockchain
        self.wallet = wallet
        self.is_mining = False

    def start_mining(self) -> None:
        self.is_mining = True
        while self.is_mining:
            # Check if there are pending transactions
            if len(self.blockchain.pending_transactions) > 0:
                print(f"Mining block {len(self.blockchain.chain)}...")
                self.blockchain.mine_pending_transactions(self.wallet.address)
                print(f"Block mined! Reward: {self.blockchain.mining_reward}")
            time.sleep(1)  # Prevent CPU overload

    def stop_mining(self) -> None:
        self.is_mining = False

    def get_mining_status(self) -> dict:
        return {
            "is_mining": self.is_mining,
            "miner_address": self.wallet.address,
            "pending_transactions": len(self.blockchain.pending_transactions),
            "current_block": len(self.blockchain.chain),
            "mining_reward": self.blockchain.mining_reward
        } 