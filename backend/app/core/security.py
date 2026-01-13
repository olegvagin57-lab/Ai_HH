"""Security utilities: JWT, password hashing, validation"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import re
from app.config import settings


class SecurityService:
    """Service for security operations"""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days
        
        # Password hashing context
        # Use bcrypt directly to avoid passlib issues
        import bcrypt
        self.bcrypt = bcrypt
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        # Truncate password to 72 bytes (bcrypt limit)
        password_bytes = password.encode('utf-8')[:72]
        salt = self.bcrypt.gensalt()
        hashed = self.bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash"""
        try:
            password_bytes = plain_password.encode('utf-8')[:72]
            hashed_bytes = hashed_password.encode('utf-8')
            return self.bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False
    
    def validate_password_strength(self, password: str) -> tuple:
        """
        Validate password strength
        Returns: (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 72:
            return False, "Password cannot be longer than 72 characters"
        
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit"
        
        return True, "Password is valid"
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        Returns: payload dict if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                return None
            
            return payload
        except JWTError:
            return None
    
    def create_session_token(self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """Create session token with user ID and additional claims"""
        data = {"sub": user_id}
        if additional_claims:
            data.update(additional_claims)
        return self.create_access_token(data)


# Global security service instance
security_service = SecurityService()
