import hashlib
import numpy as np
from typing import Tuple, List, Optional
import time
import os
import mmap
import struct
from ..config.token import get_block_reward, TOKEN_SYMBOL

class Ethash:
    def __init__(self, cache_size: int = 1024 * 1024 * 16):  # 16MB cache
        self.cache_size = cache_size
        self.cache = None
        self.cache_epoch = -1
        self.cache_file = "ethash_cache.dat"

    def get_seedhash(self, epoch: int) -> bytes:
        """Get the seed hash for a given epoch"""
        seed = b'\x00' * 32
        for _ in range(epoch):
            seed = hashlib.sha3_256(seed).digest()
        return seed

    def generate_cache(self, epoch: int) -> None:
        """Generate the cache for a given epoch"""
        if self.cache_epoch == epoch and self.cache is not None:
            return

        seed = self.get_seedhash(epoch)
        n = self.cache_size // 64
        cache = np.zeros(n, dtype=np.uint32)

        # Initialize cache
        cache[0] = int.from_bytes(hashlib.sha3_256(seed).digest()[:4], 'little')
        for i in range(1, n):
            cache[i] = int.from_bytes(
                hashlib.sha3_256(cache[i-1].tobytes()).digest()[:4],
                'little'
            )

        # Perform cache generation rounds
        for _ in range(3):
            for i in range(n):
                v = cache[i] % n
                cache[i] = cache[i] ^ cache[v]
                cache[i] = int.from_bytes(
                    hashlib.sha3_256(cache[i].tobytes()).digest()[:4],
                    'little'
                )

        self.cache = cache
        self.cache_epoch = epoch

        # Save cache to file
        with open(self.cache_file, 'wb') as f:
            f.write(cache.tobytes())

    def load_cache(self, epoch: int) -> bool:
        """Load cache from file if it exists"""
        if not os.path.exists(self.cache_file):
            return False

        try:
            with open(self.cache_file, 'rb') as f:
                cache_data = f.read()
            self.cache = np.frombuffer(cache_data, dtype=np.uint32)
            self.cache_epoch = epoch
            return True
        except:
            return False

    def hashimoto(self, header: bytes, nonce: int, full_size: int) -> Tuple[bytes, bytes]:
        """Hashimoto algorithm implementation"""
        if self.cache is None:
            raise ValueError("Cache not initialized")

        n = len(self.cache)
        mix = hashlib.sha3_256(header + nonce.to_bytes(8, 'little')).digest()
        mix = int.from_bytes(mix, 'little') % n

        for _ in range(64):
            mix = self.cache[mix] ^ int.from_bytes(mix.to_bytes(4, 'little'), 'little')
            mix = int.from_bytes(hashlib.sha3_256(mix.to_bytes(4, 'little')).digest()[:4], 'little')

        return hashlib.sha3_256(mix.to_bytes(4, 'little')).digest(), mix.to_bytes(4, 'little')

    def mine(self, header: bytes, difficulty: int, start_nonce: int = 0) -> Optional[Tuple[int, bytes]]:
        """Mine a block with the given header and difficulty"""
        epoch = int.from_bytes(header[:4], 'big') // 30000

        # Try to load cache, generate if not available
        if not self.load_cache(epoch):
            self.generate_cache(epoch)

        target = 2 ** (256 - difficulty)
        nonce = start_nonce

        while True:
            mix_digest, result = self.hashimoto(header, nonce, self.cache_size)
            if int.from_bytes(result, 'big') < target:
                return nonce, mix_digest
            nonce += 1

    def verify(self, header: bytes, nonce: int, mix_digest: bytes, difficulty: int) -> bool:
        """Verify a block's proof of work"""
        epoch = int.from_bytes(header[:4], 'big') // 30000
        if not self.load_cache(epoch):
            self.generate_cache(epoch)

        target = 2 ** (256 - difficulty)
        _, result = self.hashimoto(header, nonce, self.cache_size)
        return int.from_bytes(result, 'big') < target

class EthashMiner:
    def __init__(self, difficulty: int = 4):
        self.ethash = Ethash()
        self.difficulty = difficulty
        self.is_mining = False
        self.current_block_height = 0

    def mine_block(self, header: bytes) -> Optional[Tuple[int, bytes, int]]:
        """Mine a block with the given header"""
        result = self.ethash.mine(header, self.difficulty)
        if result:
            nonce, mix_digest = result
            reward = get_block_reward(self.current_block_height)
            self.current_block_height += 1
            return nonce, mix_digest, reward
        return None

    def verify_block(self, header: bytes, nonce: int, mix_digest: bytes) -> bool:
        """Verify a block's proof of work"""
        return self.ethash.verify(header, nonce, mix_digest, self.difficulty)

    def start_mining(self, header: bytes) -> None:
        """Start mining with the given header"""
        self.is_mining = True
        while self.is_mining:
            result = self.mine_block(header)
            if result:
                nonce, mix_digest, reward = result
                print(f"Block found! Nonce: {nonce}")
                print(f"Mix digest: {mix_digest.hex()}")
                print(f"Mining reward: {reward} {TOKEN_SYMBOL}")
                break
            time.sleep(0.1)  # Prevent CPU overload

    def stop_mining(self) -> None:
        """Stop mining"""
        self.is_mining = False

    def get_current_reward(self) -> int:
        """Get the current block reward"""
        return get_block_reward(self.current_block_height) 