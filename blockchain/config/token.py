from typing import Dict, Any

# Token name and symbol
TOKEN_NAME = "Xugenping"
TOKEN_SYMBOL = "XGP"

# Total supply
TOTAL_SUPPLY = 19840228

# Initial block reward
INITIAL_BLOCK_REWARD = 50

# Halving period in blocks (assuming 10 minutes per block)
HALVING_PERIOD = 6 * 30 * 24 * 6  # 6 months * 30 days * 24 hours * 6 blocks per hour

# Block time in seconds
BLOCK_TIME = 600  # 10 minutes

def get_block_reward(block_height: int) -> int:
    """Calculate block reward based on block height"""
    halvings = block_height // HALVING_PERIOD
    reward = INITIAL_BLOCK_REWARD
    
    # Apply halvings
    for _ in range(halvings):
        reward = reward // 2
        
    return reward

def get_total_supply_at_height(block_height: int) -> int:
    """Calculate total supply at given block height"""
    total = 0
    current_height = 0
    
    while current_height <= block_height:
        reward = get_block_reward(current_height)
        total += reward
        current_height += 1
        
    return min(total, TOTAL_SUPPLY) 