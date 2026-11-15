import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_key() -> bytes:
    b64 = os.environ.get("NOTES_ENCRYPTION_KEY_B64")
    if not b64:
        raise RuntimeError("NOTES_ENCRYPTION_KEY_B64 not set")
    key = base64.b64decode(b64)
    if len(key) != 32:
        raise RuntimeError("NOTES_ENCRYPTION_KEY_B64 must decode to 32 bytes")
    return key


def encrypt(plaintext: str) -> bytes:
    nonce = os.urandom(12)
    ct = AESGCM(_get_key()).encrypt(nonce, plaintext.encode("utf-8"), None)
    return nonce + ct  # nonce(12) | ciphertext+tag


def decrypt(blob: bytes) -> str:
    if not blob or len(blob) < 12 + 16:
        raise ValueError("invalid ciphertext")
    nonce, ct = blob[:12], blob[12:]
    pt = AESGCM(_get_key()).decrypt(nonce, ct, None)
    return pt.decode("utf-8")
