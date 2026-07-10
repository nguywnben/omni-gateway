"""Password hashing helpers for control-panel authentication."""

from __future__ import annotations

import base64
import binascii
import hashlib
import secrets


PASSWORD_HASH_SCHEME = "scrypt"
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
SALT_BYTES = 16
KEY_BYTES = 32


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode(value: str) -> bytes:
    padding = "=" * ((4 - len(value) % 4) % 4)
    return base64.urlsafe_b64decode(value + padding)


def hash_password(password: str) -> str:
    """Hash a password with a unique salt and bounded scrypt parameters."""
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=KEY_BYTES,
    )
    return "$".join(
        (
            PASSWORD_HASH_SCHEME,
            str(SCRYPT_N),
            str(SCRYPT_R),
            str(SCRYPT_P),
            _encode(salt),
            _encode(digest),
        )
    )


def is_password_hash(value: str) -> bool:
    return str(value or "").startswith(f"{PASSWORD_HASH_SCHEME}$")


def verify_password_value(candidate: str, stored_value: str) -> bool:
    """Verify scrypt values while retaining plaintext legacy compatibility."""
    stored = str(stored_value or "")
    if not is_password_hash(stored):
        return secrets.compare_digest(candidate, stored)

    try:
        scheme, n, r, p, encoded_salt, encoded_digest = stored.split("$", 5)
        if scheme != PASSWORD_HASH_SCHEME:
            return False
        parsed_n, parsed_r, parsed_p = int(n), int(r), int(p)
        if (parsed_n, parsed_r, parsed_p) != (SCRYPT_N, SCRYPT_R, SCRYPT_P):
            return False
        salt = _decode(encoded_salt)
        expected = _decode(encoded_digest)
        if len(salt) != SALT_BYTES or len(expected) != KEY_BYTES:
            return False
        actual = hashlib.scrypt(
            candidate.encode("utf-8"),
            salt=salt,
            n=parsed_n,
            r=parsed_r,
            p=parsed_p,
            dklen=len(expected),
        )
        return secrets.compare_digest(actual, expected)
    except (binascii.Error, TypeError, ValueError, OverflowError):
        return False
