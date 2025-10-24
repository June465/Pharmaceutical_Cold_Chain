# node/src/crypto/wallet.py
from Crypto.Hash import keccak
from ecdsa import SigningKey, VerifyingKey, SECP256k1

class Wallet:
    def __init__(self, private_key_bytes=None):
        self.signing_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1) if private_key_bytes else SigningKey.generate(curve=SECP256k1)
        self.verifying_key = self.signing_key.get_verifying_key()

    @property
    def private_key(self): return self.signing_key.to_string().hex()
    @property
    def public_key(self): return self.verifying_key.to_string('uncompressed').hex()
    @property
    def address(self):
        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(self.verifying_key.to_string('uncompressed'))
        return '0x' + keccak_hash.digest()[-20:].hex()

def hash_data(data: str):
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(data.encode('utf-8'))
    return keccak_hash.digest()

def sign_data(wallet: Wallet, data_hash: bytes):
    return wallet.signing_key.sign_digest(data_hash).hex()

def verify_signature(public_key_hex, signature_hex, data_hash):
    try:
        verifying_key = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1, hashfunc=None)
        return verifying_key.verify_digest(bytes.fromhex(signature_hex), data_hash)
    except Exception:
        return False