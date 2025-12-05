import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import redis
import secrets
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    PREMIUM = "premium"
    BASIC = "basic"
    GUEST = "guest"

class User(BaseModel):
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None

class TokenData(BaseModel):
    user_id: str
    username: str
    role: str
    exp: datetime

class AuthManager:
    """Authentication and authorization manager"""
    
    def __init__(self, secret_key: str, redis_url: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(hours=24)
        self.refresh_token_expire = timedelta(days=7)
        self.redis_client = redis.from_url(redis_url)
        self.security = HTTPBearer()
        
        # Rate limiting
        self.rate_limits = {
            UserRole.GUEST: {"requests_per_hour": 100, "requests_per_day": 1000},
            UserRole.BASIC: {"requests_per_hour": 500, "requests_per_day": 5000},
            UserRole.PREMIUM: {"requests_per_hour": 2000, "requests_per_day": 20000},
            UserRole.ADMIN: {"requests_per_hour": 10000, "requests_per_day": 100000}
        }
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + self.access_token_expire
        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + self.refresh_token_expire
        payload = {
            "user_id": user.id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token in Redis
        self.redis_client.setex(
            f"refresh_token:{user.id}",
            int(self.refresh_token_expire.total_seconds()),
            token
        )
        
        return token
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return TokenData(
                user_id=payload["user_id"],
                username=payload["username"],
                role=payload["role"],
                exp=datetime.fromtimestamp(payload["exp"])
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def generate_api_key(self, user_id: str) -> str:
        """Generate API key for user"""
        api_key = f"sk_{secrets.token_urlsafe(32)}"
        
        # Store API key in Redis with user info
        self.redis_client.setex(
            f"api_key:{api_key}",
            int(timedelta(days=365).total_seconds()),  # 1 year expiry
            user_id
        )
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """Verify API key and return user ID"""
        user_id = self.redis_client.get(f"api_key:{api_key}")
        return user_id.decode() if user_id else None
    
    def revoke_api_key(self, api_key: str):
        """Revoke API key"""
        self.redis_client.delete(f"api_key:{api_key}")
    
    def check_rate_limit(self, user_id: str, role: UserRole) -> bool:
        """Check if user is within rate limits"""
        now = datetime.now()
        hour_key = f"rate_limit:hour:{user_id}:{now.strftime('%Y%m%d%H')}"
        day_key = f"rate_limit:day:{user_id}:{now.strftime('%Y%m%d')}"
        
        limits = self.rate_limits[role]
        
        # Check hourly limit
        hourly_count = self.redis_client.get(hour_key)
        if hourly_count and int(hourly_count) >= limits["requests_per_hour"]:
            return False
        
        # Check daily limit
        daily_count = self.redis_client.get(day_key)
        if daily_count and int(daily_count) >= limits["requests_per_day"]:
            return False
        
        # Increment counters
        pipe = self.redis_client.pipeline()
        pipe.incr(hour_key)
        pipe.expire(hour_key, 3600)  # 1 hour
        pipe.incr(day_key)
        pipe.expire(day_key, 86400)  # 1 day
        pipe.execute()
        
        return True
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> User:
        """Get current authenticated user"""
        token = credentials.credentials
        
        # Try JWT token first
        try:
            token_data = self.verify_token(token)
            
            # Get user from database (simplified - would query actual DB)
            user = User(
                id=token_data.user_id,
                username=token_data.username,
                email=f"{token_data.username}@example.com",
                role=UserRole(token_data.role),
                created_at=datetime.now()
            )
            
            # Check rate limits
            if not self.check_rate_limit(user.id, user.role):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            return user
            
        except HTTPException:
            # Try API key
            if token.startswith("sk_"):
                user_id = self.verify_api_key(token)
                if user_id:
                    # Get user from database (simplified)
                    user = User(
                        id=user_id,
                        username=f"api_user_{user_id}",
                        email=f"api_{user_id}@example.com",
                        role=UserRole.BASIC,  # Default role for API keys
                        created_at=datetime.now()
                    )
                    
                    if not self.check_rate_limit(user.id, user.role):
                        raise HTTPException(
                            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                            detail="Rate limit exceeded"
                        )
                    
                    return user
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

class RoleChecker:
    """Role-based access control"""
    
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(AuthManager.get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user

# Convenience functions for common role checks
require_admin = RoleChecker([UserRole.ADMIN])
require_premium = RoleChecker([UserRole.ADMIN, UserRole.PREMIUM])
require_basic = RoleChecker([UserRole.ADMIN, UserRole.PREMIUM, UserRole.BASIC])
require_any = RoleChecker([UserRole.ADMIN, UserRole.PREMIUM, UserRole.BASIC, UserRole.GUEST])