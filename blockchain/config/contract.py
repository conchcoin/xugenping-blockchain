from typing import Dict, Any

# Gas price constants (in XGP)
MIN_GAS_PRICE = 0.00001  # Minimum gas price
MAX_GAS_PRICE = 0.001    # Maximum gas price
DEFAULT_GAS_PRICE = 0.0001  # Default gas price

# Gas limits for different operations
GAS_LIMITS = {
    'deploy_contract': 1000000,    # Gas limit for contract deployment
    'execute_contract': 100000,    # Gas limit for contract execution
    'transfer': 21000,             # Gas limit for simple transfer
    'store_data': 20000,           # Gas limit for storing data
    'load_data': 5000,             # Gas limit for loading data
    'compute': 1000,               # Gas limit for computation
}

# Contract deployment fee (in XGP)
CONTRACT_DEPLOYMENT_FEE = 1.0

def calculate_gas_cost(gas_used: int, gas_price: float) -> float:
    """Calculate the total gas cost"""
    return gas_used * gas_price

def calculate_contract_deployment_cost(gas_price: float = DEFAULT_GAS_PRICE) -> float:
    """Calculate the total cost for contract deployment"""
    gas_cost = calculate_gas_cost(GAS_LIMITS['deploy_contract'], gas_price)
    return gas_cost + CONTRACT_DEPLOYMENT_FEE

def validate_gas_price(gas_price: float) -> float:
    """Validate and adjust gas price if necessary"""
    if gas_price < MIN_GAS_PRICE:
        return MIN_GAS_PRICE
    if gas_price > MAX_GAS_PRICE:
        return MAX_GAS_PRICE
    return gas_price 