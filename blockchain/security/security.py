from typing import Dict, Any, List, Optional
import hashlib
import hmac
import time
import json
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad

class SecurityManager:
    def __init__(self):
        self.salt = get_random_bytes(16)
        self.key = None
        self.encrypted_data = {}

    def derive_key(self, password: str) -> bytes:
        """Derive a key from a password using PBKDF2"""
        return PBKDF2(
            password.encode(),
            self.salt,
            dkLen=32,
            count=100000
        )

    def encrypt_data(self, data: Dict[str, Any], password: str) -> bytes:
        """Encrypt data using AES-256-GCM"""
        if not self.key:
            self.key = self.derive_key(password)

        # Convert data to JSON
        json_data = json.dumps(data).encode()

        # Generate a random IV
        iv = get_random_bytes(12)

        # Create cipher
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=iv)

        # Encrypt the data
        ciphertext, tag = cipher.encrypt_and_digest(pad(json_data, AES.block_size))

        # Combine IV, tag, and ciphertext
        encrypted_data = iv + tag + ciphertext
        return encrypted_data

    def decrypt_data(self, encrypted_data: bytes, password: str) -> Dict[str, Any]:
        """Decrypt data using AES-256-GCM"""
        if not self.key:
            self.key = self.derive_key(password)

        # Extract IV, tag, and ciphertext
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]

        # Create cipher
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=iv)

        # Decrypt the data
        try:
            decrypted_data = unpad(cipher.decrypt_and_verify(ciphertext, tag), AES.block_size)
            return json.loads(decrypted_data.decode())
        except (ValueError, KeyError):
            raise ValueError("Invalid password or corrupted data")

class TransactionSecurity:
    def __init__(self):
        self.replay_protection = {}
        self.max_replay_window = 3600  # 1 hour

    def add_replay_protection(self, transaction_hash: str) -> None:
        """Add a transaction to replay protection"""
        self.replay_protection[transaction_hash] = time.time()

    def check_replay_protection(self, transaction_hash: str) -> bool:
        """Check if a transaction is protected from replay attacks"""
        if transaction_hash in self.replay_protection:
            # Check if the transaction is still within the replay window
            if time.time() - self.replay_protection[transaction_hash] > self.max_replay_window:
                del self.replay_protection[transaction_hash]
                return False
            return True
        return False

    def clean_expired_protection(self) -> None:
        """Clean up expired replay protection entries"""
        current_time = time.time()
        expired = [
            tx_hash for tx_hash, timestamp in self.replay_protection.items()
            if current_time - timestamp > self.max_replay_window
        ]
        for tx_hash in expired:
            del self.replay_protection[tx_hash]

class BlockSecurity:
    def __init__(self):
        self.block_timestamps = {}
        self.min_block_time = 15  # Minimum seconds between blocks

    def check_block_timing(self, block_hash: str, timestamp: float) -> bool:
        """Check if a block's timing is valid"""
        if not self.block_timestamps:
            self.block_timestamps[block_hash] = timestamp
            return True

        last_timestamp = max(self.block_timestamps.values())
        if timestamp - last_timestamp < self.min_block_time:
            return False

        self.block_timestamps[block_hash] = timestamp
        return True

    def clean_old_timestamps(self, max_age: int = 3600) -> None:
        """Clean up old block timestamps"""
        current_time = time.time()
        expired = [
            block_hash for block_hash, timestamp in self.block_timestamps.items()
            if current_time - timestamp > max_age
        ]
        for block_hash in expired:
            del self.block_timestamps[block_hash]

class NetworkSecurity:
    def __init__(self):
        self.peer_blacklist = set()
        self.rate_limits = {}
        self.max_requests = 100  # Maximum requests per minute
        self.rate_limit_window = 60  # 1 minute window

    def add_to_blacklist(self, peer_address: str) -> None:
        """Add a peer to the blacklist"""
        self.peer_blacklist.add(peer_address)

    def is_blacklisted(self, peer_address: str) -> bool:
        """Check if a peer is blacklisted"""
        return peer_address in self.peer_blacklist

    def check_rate_limit(self, peer_address: str) -> bool:
        """Check if a peer has exceeded the rate limit"""
        current_time = time.time()
        if peer_address not in self.rate_limits:
            self.rate_limits[peer_address] = []

        # Remove old requests
        self.rate_limits[peer_address] = [
            t for t in self.rate_limits[peer_address]
            if current_time - t < self.rate_limit_window
        ]

        # Check if the peer has exceeded the rate limit
        if len(self.rate_limits[peer_address]) >= self.max_requests:
            return False

        # Add the current request
        self.rate_limits[peer_address].append(current_time)
        return True

    def clean_rate_limits(self) -> None:
        """Clean up old rate limit entries"""
        current_time = time.time()
        for peer_address in list(self.rate_limits.keys()):
            self.rate_limits[peer_address] = [
                t for t in self.rate_limits[peer_address]
                if current_time - t < self.rate_limit_window
            ]
            if not self.rate_limits[peer_address]:
                del self.rate_limits[peer_address] 