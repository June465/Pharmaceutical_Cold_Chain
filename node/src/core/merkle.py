# node/src/core/merkle.py
import math
from typing import List
from src.crypto.wallet import hash_data

def build_merkle_root(items: List[str]) -> str:
    """
    Builds a Merkle tree from a list of items (e.g., transaction hashes)
    and returns the Merkle root hash.
    """
    if not items:
        return hash_data('').hex() # A default hash for an empty list

    # Create the first level of leaves
    leaves = [hash_data(item) for item in items]

    while len(leaves) > 1:
        # If the number of leaves is odd, duplicate the last one
        if len(leaves) % 2 != 0:
            leaves.append(leaves[-1])
        
        new_level = []
        # Pair up leaves and hash them together
        for i in range(0, len(leaves), 2):
            combined_hash = leaves[i] + leaves[i+1]
            new_level.append(hash_data(combined_hash.hex()))
        
        leaves = new_level
        
    return leaves[0].hex()