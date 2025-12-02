import hashlib
from datetime import datetime

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user."""
    return hash_password(plain_password) == hashed_password

def get_current_timestamp() -> str:
    """Returns ISO formatted timestamp."""
    return datetime.utcnow().isoformat()