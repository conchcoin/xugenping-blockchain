from flask import Blueprint, request, jsonify
from typing import Dict, Any
from ..contracts.vm import Contract, ContractRegistry
from ..config.contract import validate_gas_price, DEFAULT_GAS_PRICE

contract_api = Blueprint('contract_api', __name__)
contract_registry = ContractRegistry()

@contract_api.route('/deploy', methods=['POST'])
def deploy_contract():
    """Deploy a new contract"""
    try:
        data = request.get_json()
        if not data or 'name' not in data or 'code' not in data or 'creator' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        gas_price = validate_gas_price(float(data.get('gas_price', DEFAULT_GAS_PRICE)))
        contract = Contract(
            name=data['name'],
            code=bytes.fromhex(data['code']),
            creator=data['creator']
        )

        address, cost = contract_registry.deploy(contract, gas_price)
        return jsonify({
            'success': True,
            'contract_address': address,
            'deployment_cost': cost
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_api.route('/execute/<contract_address>', methods=['POST'])
def execute_contract(contract_address: str):
    """Execute a contract"""
    try:
        data = request.get_json()
        if not data or 'input_data' not in data:
            return jsonify({'error': 'Missing input data'}), 400

        gas_price = validate_gas_price(float(data.get('gas_price', DEFAULT_GAS_PRICE)))
        result, cost = contract_registry.execute(
            contract_address,
            bytes.fromhex(data['input_data']),
            gas_price
        )

        return jsonify({
            'success': True,
            'result': result,
            'execution_cost': cost
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_api.route('/state/<contract_address>', methods=['GET'])
def get_contract_state(contract_address: str):
    """Get contract state"""
    try:
        state = contract_registry.get_contract_state(contract_address)
        return jsonify({
            'success': True,
            'state': state
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_api.route('/info/<contract_address>', methods=['GET'])
def get_contract_info(contract_address: str):
    """Get contract information"""
    try:
        contract = contract_registry.get_contract(contract_address)
        if not contract:
            return jsonify({'error': 'Contract not found'}), 404

        return jsonify({
            'success': True,
            'contract': contract.to_dict()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contract_api.route('/estimate-gas', methods=['POST'])
def estimate_gas():
    """Estimate gas cost for contract deployment or execution"""
    try:
        data = request.get_json()
        if not data or 'operation' not in data:
            return jsonify({'error': 'Missing operation type'}), 400

        operation = data['operation']
        gas_price = validate_gas_price(float(data.get('gas_price', DEFAULT_GAS_PRICE)))

        if operation == 'deploy':
            if 'code' not in data:
                return jsonify({'error': 'Missing contract code'}), 400
            # Simulate deployment to estimate gas
            contract = Contract(
                name=data.get('name', 'TestContract'),
                code=bytes.fromhex(data['code']),
                creator=data.get('creator', '0x0')
            )
            _, cost = contract_registry.deploy(contract, gas_price)
            return jsonify({
                'success': True,
                'estimated_cost': cost
            })

        elif operation == 'execute':
            if 'contract_address' not in data or 'input_data' not in data:
                return jsonify({'error': 'Missing required fields'}), 400
            # Simulate execution to estimate gas
            _, cost = contract_registry.execute(
                data['contract_address'],
                bytes.fromhex(data['input_data']),
                gas_price
            )
            return jsonify({
                'success': True,
                'estimated_cost': cost
            })

        else:
            return jsonify({'error': 'Invalid operation'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500 