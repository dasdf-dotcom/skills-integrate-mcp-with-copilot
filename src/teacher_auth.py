import hashlib
import hmac
import json
import secrets
from pathlib import Path


PASSWORD_HASH_ITERATIONS = 600_000


def hash_password(password: str, salt: bytes | None = None) -> dict[str, str]:
    salt = salt or secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
    )
    return {"salt": salt.hex(), "password_hash": password_hash.hex()}


def verify_teacher(username: str, password: str, teachers_file: Path) -> bool:
    try:
        teacher_data = json.loads(teachers_file.read_text(encoding="utf-8"))
        credential = teacher_data.get("teachers", {}).get(username)
        salt = bytes.fromhex(credential["salt"])
        expected_hash = bytes.fromhex(credential["password_hash"])
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False

    actual_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
    )
    return hmac.compare_digest(actual_hash, expected_hash)