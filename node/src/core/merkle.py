# node/src/core/merkle.py
from ..crypto.wallet import hash_data

def build_merkle_root(items):
    if not items:
        return hash_data('').hex()

    leaves = [hash_data(item) for item in items]
    while len(leaves) > 1:
        if len(leaves) % 2 != 0:
            leaves.append(leaves[-1])
        new_level = [hash_data((leaves[i] + leaves[i+1]).hex()) for i in range(0, len(leaves), 2)]
        leaves = new_level
    return leaves[0].hex()