from typing import Dict, Any, List, Optional, Tuple
import json
import hashlib
from enum import Enum
from ..config.contract import GAS_LIMITS, calculate_gas_cost, validate_gas_price
import time

class OpCode(Enum):
    PUSH = 0x60
    POP = 0x50
    ADD = 0x01
    SUB = 0x02
    MUL = 0x03
    DIV = 0x04
    STORE = 0x52
    LOAD = 0x51
    JUMP = 0x56
    JUMPI = 0x57
    STOP = 0x00

class ContractVM:
    def __init__(self):
        self.stack: List[int] = []
        self.memory: Dict[str, Any] = {}
        self.pc: int = 0  # Program counter
        self.contracts: Dict[str, bytes] = {}
        self.gas_used: int = 0
        self.gas_price: float = 0.0

    def deploy_contract(self, contract_code: bytes, contract_address: str, gas_price: float) -> Tuple[bool, float]:
        """Deploy a new contract"""
        self.gas_price = validate_gas_price(gas_price)
        self.gas_used = 0
        
        try:
            # Simulate contract deployment
            self.contracts[contract_address] = contract_code
            self.gas_used = GAS_LIMITS['deploy_contract']
            return True, calculate_gas_cost(self.gas_used, self.gas_price)
        except Exception as e:
            return False, 0.0

    def execute_contract(self, contract_address: str, input_data: bytes, gas_price: float) -> Tuple[Any, float]:
        """Execute a contract with input data"""
        if contract_address not in self.contracts:
            raise ValueError(f"Contract not found: {contract_address}")

        self.gas_price = validate_gas_price(gas_price)
        self.gas_used = 0
        self.pc = 0
        self.stack = []
        self.memory = {}

        contract_code = self.contracts[contract_address]
        result = None

        try:
            while self.pc < len(contract_code) and self.gas_used < GAS_LIMITS['execute_contract']:
                opcode = contract_code[self.pc]
                self.pc += 1
                self.gas_used += GAS_LIMITS['compute']

                if opcode == OpCode.PUSH.value:
                    value = int.from_bytes(contract_code[self.pc:self.pc+32], 'big')
                    self.pc += 32
                    self.stack.append(value)
                    self.gas_used += GAS_LIMITS['store_data']

                elif opcode == OpCode.POP.value:
                    if self.stack:
                        self.stack.pop()
                        self.gas_used += GAS_LIMITS['compute']

                elif opcode == OpCode.ADD.value:
                    if len(self.stack) >= 2:
                        a = self.stack.pop()
                        b = self.stack.pop()
                        self.stack.append(a + b)
                        self.gas_used += GAS_LIMITS['compute']

                elif opcode == OpCode.SUB.value:
                    if len(self.stack) >= 2:
                        a = self.stack.pop()
                        b = self.stack.pop()
                        self.stack.append(a - b)
                        self.gas_used += GAS_LIMITS['compute']

                elif opcode == OpCode.MUL.value:
                    if len(self.stack) >= 2:
                        a = self.stack.pop()
                        b = self.stack.pop()
                        self.stack.append(a * b)
                        self.gas_used += GAS_LIMITS['compute']

                elif opcode == OpCode.DIV.value:
                    if len(self.stack) >= 2:
                        a = self.stack.pop()
                        b = self.stack.pop()
                        if b != 0:
                            self.stack.append(a // b)
                            self.gas_used += GAS_LIMITS['compute']
                        else:
                            raise ValueError("Division by zero")

                elif opcode == OpCode.STORE.value:
                    if len(self.stack) >= 2:
                        key = str(self.stack.pop())
                        value = self.stack.pop()
                        self.memory[key] = value
                        self.gas_used += GAS_LIMITS['store_data']

                elif opcode == OpCode.LOAD.value:
                    if self.stack:
                        key = str(self.stack.pop())
                        if key in self.memory:
                            self.stack.append(self.memory[key])
                            self.gas_used += GAS_LIMITS['load_data']

                elif opcode == OpCode.JUMP.value:
                    if self.stack:
                        self.pc = self.stack.pop()
                        self.gas_used += GAS_LIMITS['compute']

                elif opcode == OpCode.JUMPI.value:
                    if len(self.stack) >= 2:
                        condition = self.stack.pop()
                        jump_to = self.stack.pop()
                        if condition:
                            self.pc = jump_to
                            self.gas_used += GAS_LIMITS['compute']

                elif opcode == OpCode.STOP.value:
                    break

            result = self.stack[-1] if self.stack else None
            return result, calculate_gas_cost(self.gas_used, self.gas_price)

        except Exception as e:
            return None, calculate_gas_cost(self.gas_used, self.gas_price)

    def get_contract_state(self, contract_address: str) -> Dict[str, Any]:
        """Get the current state of a contract"""
        if contract_address not in self.contracts:
            raise ValueError(f"Contract not found: {contract_address}")
        return self.memory.copy()

class Contract:
    def __init__(self, name: str, code: bytes, creator: str):
        self.name = name
        self.code = code
        self.creator = creator
        self.address = self._generate_address()
        self.deployment_time = time.time()

    def _generate_address(self) -> str:
        """Generate a unique contract address"""
        return hashlib.sha256(self.code).hexdigest()[:40]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'address': self.address,
            'code': self.code.hex(),
            'creator': self.creator,
            'deployment_time': self.deployment_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contract':
        return cls(
            name=data['name'],
            code=bytes.fromhex(data['code']),
            creator=data['creator']
        )

class ContractRegistry:
    def __init__(self):
        self.contracts: Dict[str, Contract] = {}
        self.vm = ContractVM()

    def deploy(self, contract: Contract, gas_price: float) -> Tuple[str, float]:
        """Deploy a new contract"""
        success, cost = self.vm.deploy_contract(contract.code, contract.address, gas_price)
        if success:
            self.contracts[contract.address] = contract
        return contract.address, cost

    def execute(self, contract_address: str, input_data: bytes, gas_price: float) -> Tuple[Any, float]:
        """Execute a contract"""
        if contract_address not in self.contracts:
            raise ValueError(f"Contract not found: {contract_address}")
        return self.vm.execute_contract(contract_address, input_data, gas_price)

    def get_contract(self, contract_address: str) -> Optional[Contract]:
        """Get a contract by address"""
        return self.contracts.get(contract_address)

    def get_contract_state(self, contract_address: str) -> Dict[str, Any]:
        """Get the current state of a contract"""
        return self.vm.get_contract_state(contract_address) 