"""认证服务"""
from datetime import datetime, timedelta, UTC
from typing import Optional
import hashlib
import bcrypt
from jose import JWTError, jwt
from app.config import get_settings

settings = get_settings()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    preprocessed = hashlib.sha256(plain_password.encode()).hexdigest()
    return bcrypt.checkpw(preprocessed.encode(), hashed_password.encode())


def get_password_hash(password: str) -> str:
    """获取密码哈希（SHA256 + bcrypt）"""
    preprocessed = hashlib.sha256(password.encode()).hexdigest()
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(preprocessed.encode(), salt).decode()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码 JWT token"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None

