import os
import binascii
from Crypto.Hash import keccak
from ecdsa import SigningKey, VerifyingKey, SECP256k1 

class Wallet:
    """
    Represents a user's wallet, containing a private/public key pair.
    """
    def __init__(self, private_key_bytes=None):
        if private_key_bytes:
            self.signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        else: 
            self.signing_key = SigningKey.generate(curve=SECP256k1)
        
        self.verifying_key = self.signing_key.get_verifying_key()

    @property
    def private_key(self) -> str:
        return self.signing_key.to_string().hex()

    @property
    def public_key(self) -> str:
        return self.verifying_key.to_string('uncompressed').hex()

    @property
    def address(self) -> str:
        pub_key_bytes = self.verifying_key.to_string('uncompressed')
        
        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(pub_key_bytes)

        address_bytes = keccak_hash.digest()[-20:]
        return '0x' + address_bytes.hex()

def hash_data(data: str) -> bytes:
    """
    Hashes the given string data using Keccak-256.
    Returns the hash as bytes.
    """
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(data.encode('utf-8'))
    return keccak_hash.digest()

def sign_data(wallet: Wallet, data_hash: bytes) -> str:
    signature_bytes = wallet.signing_key.sign_digest(data_hash)
    return signature_bytes.hex()

def verify_signature(public_key_hex: str, signature_hex: str, data_hash: bytes) -> bool:
    try:
        pub_key_bytes = bytes.fromhex(public_key_hex)
        verifying_key = VerifyingKey.from_string(pub_key_bytes, curve=SECP256k1)
        
        signature_bytes = bytes.fromhex(signature_hex)
        
        return verifying_key.verify_digest(signature_bytes, data_hash)
    except Exception as e:
        print(f"Error during verification: {e}")
        return False