from enum import Enum
from typing import Dict, List, Any, Set
import time
import json
import hashlib
from ..core.block import Block

class MessageType(Enum):
    REQUEST = 'REQUEST'
    PRE_PREPARE = 'PRE_PREPARE'
    PREPARE = 'PREPARE'
    COMMIT = 'COMMIT'
    REPLY = 'REPLY'

class PBFTNode:
    def __init__(self, node_id: str, nodes: List[str]):
        self.node_id = node_id
        self.nodes = nodes  # List of all node IDs
        self.n = len(nodes)  # Total number of nodes
        self.f = (self.n - 1) // 3  # Maximum number of faulty nodes
        
        # State
        self.view = 0
        self.seq_num = 0
        self.primary = self.nodes[self.view % self.n]
        
        # Message logs
        self.request_log: Dict[str, Dict] = {}
        self.pre_prepare_log: Dict[str, Dict] = {}
        self.prepare_log: Dict[str, Dict] = {}
        self.commit_log: Dict[str, Dict] = {}
        
        # Message counters
        self.prepare_count: Dict[str, int] = {}
        self.commit_count: Dict[str, int] = {}
        
        # Block cache
        self.block_cache: Dict[str, Block] = {}

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a client request"""
        if self.node_id != self.primary:
            return {'type': 'error', 'message': 'Not primary node'}
        
        # Generate request ID
        request_id = self._generate_request_id(request)
        
        # Create pre-prepare message
        pre_prepare = {
            'type': MessageType.PRE_PREPARE,
            'view': self.view,
            'seq_num': self.seq_num,
            'request_id': request_id,
            'request': request,
            'digest': self._hash_request(request)
        }
        
        # Log the request and pre-prepare message
        self.request_log[request_id] = request
        self.pre_prepare_log[request_id] = pre_prepare
        
        # Broadcast pre-prepare message
        return pre_prepare

    def handle_pre_prepare(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a pre-prepare message"""
        # Verify the message
        if not self._verify_pre_prepare(message):
            return {'type': 'error', 'message': 'Invalid pre-prepare message'}
        
        request_id = message['request_id']
        request = message['request']
        
        # Log the request and pre-prepare message
        self.request_log[request_id] = request
        self.pre_prepare_log[request_id] = message
        
        # Create prepare message
        prepare = {
            'type': MessageType.PREPARE,
            'view': self.view,
            'seq_num': message['seq_num'],
            'request_id': request_id,
            'digest': message['digest']
        }
        
        # Initialize prepare counter
        self.prepare_count[request_id] = 1
        
        return prepare

    def handle_prepare(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a prepare message"""
        # Verify the message
        if not self._verify_prepare(message):
            return {'type': 'error', 'message': 'Invalid prepare message'}
        
        request_id = message['request_id']
        
        # Update prepare counter
        self.prepare_count[request_id] = self.prepare_count.get(request_id, 0) + 1
        
        # Check if we have enough prepare messages
        if self.prepare_count[request_id] >= 2 * self.f + 1:
            # Create commit message
            commit = {
                'type': MessageType.COMMIT,
                'view': self.view,
                'seq_num': message['seq_num'],
                'request_id': request_id,
                'digest': message['digest']
            }
            
            # Initialize commit counter
            self.commit_count[request_id] = 1
            
            return commit
        
        return None

    def handle_commit(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a commit message"""
        # Verify the message
        if not self._verify_commit(message):
            return {'type': 'error', 'message': 'Invalid commit message'}
        
        request_id = message['request_id']
        
        # Update commit counter
        self.commit_count[request_id] = self.commit_count.get(request_id, 0) + 1
        
        # Check if we have enough commit messages
        if self.commit_count[request_id] >= 2 * self.f + 1:
            # Execute the request
            request = self.request_log[request_id]
            return self._execute_request(request)
        
        return None

    def _verify_pre_prepare(self, message: Dict[str, Any]) -> bool:
        """Verify a pre-prepare message"""
        # Check if the primary is correct
        if message['view'] % self.n != self.nodes.index(self.primary):
            return False
        
        # Check if the request hash matches
        request = message['request']
        if message['digest'] != self._hash_request(request):
            return False
        
        return True

    def _verify_prepare(self, message: Dict[str, Any]) -> bool:
        """Verify a prepare message"""
        request_id = message['request_id']
        
        # Check if we have the corresponding pre-prepare message
        if request_id not in self.pre_prepare_log:
            return False
        
        pre_prepare = self.pre_prepare_log[request_id]
        
        # Check if the view and sequence number match
        if (message['view'] != pre_prepare['view'] or 
            message['seq_num'] != pre_prepare['seq_num'] or
            message['digest'] != pre_prepare['digest']):
            return False
        
        return True

    def _verify_commit(self, message: Dict[str, Any]) -> bool:
        """Verify a commit message"""
        request_id = message['request_id']
        
        # Check if we have the corresponding pre-prepare message
        if request_id not in self.pre_prepare_log:
            return False
        
        pre_prepare = self.pre_prepare_log[request_id]
        
        # Check if the view and sequence number match
        if (message['view'] != pre_prepare['view'] or 
            message['seq_num'] != pre_prepare['seq_num'] or
            message['digest'] != pre_prepare['digest']):
            return False
        
        return True

    def _execute_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a request and return the result"""
        # This is where you would execute the actual request
        # For example, adding a block to the blockchain
        return {
            'type': MessageType.REPLY,
            'view': self.view,
            'request_id': self._generate_request_id(request),
            'result': 'success'
        }

    def _generate_request_id(self, request: Dict[str, Any]) -> str:
        """Generate a unique request ID"""
        request_str = json.dumps(request, sort_keys=True)
        return hashlib.sha256(request_str.encode()).hexdigest()

    def _hash_request(self, request: Dict[str, Any]) -> str:
        """Hash a request"""
        request_str = json.dumps(request, sort_keys=True)
        return hashlib.sha256(request_str.encode()).hexdigest()

    def change_view(self) -> None:
        """Change the view (primary node)"""
        self.view += 1
        self.primary = self.nodes[self.view % self.n]
        # Reset message logs and counters
        self.request_log.clear()
        self.pre_prepare_log.clear()
        self.prepare_log.clear()
        self.commit_log.clear()
        self.prepare_count.clear()
        self.commit_count.clear() 