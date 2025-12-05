# API Authentication

## Overview

Authentication and authorization mechanisms for the Stock AI API service.

**Status**: 📋 **PLANNED** - Implementation in Phase 6

## Authentication Methods

### 1. JWT Token Authentication

#### Token Generation
```python
# services/api/src/auth/jwt_handler.py
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

class JWTHandler:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=30)
        
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload if payload.get("exp") > datetime.utcnow().timestamp() else None
        except JWTError:
            return None
```

#### Login Endpoint
```python
# services/api/src/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

@router.post("/auth/login")
async def login(credentials: UserCredentials):
    user = await authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = jwt_handler.create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 1800,  # 30 minutes
        "user": {
            "username": user.username,
            "role": user.role
        }
    }

@router.post("/auth/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    new_token = jwt_handler.create_access_token(
        data={"sub": current_user["sub"], "user_id": current_user["user_id"]}
    )
    return {"access_token": new_token, "token_type": "bearer"}
```

#### Usage
```bash
# Login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password123"}'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}

# Use token in requests
curl -X GET "http://localhost:8000/api/v1/stocks/VCB" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 2. API Key Authentication

#### API Key Management
```python
# services/api/src/auth/api_key_handler.py
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import secrets

class APIKeyHandler:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def generate_api_key(self, user_id: str, name: str = None) -> str:
        # Generate secure random key
        key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        # Store key metadata
        key_data = {
            "user_id": user_id,
            "name": name or "Default",
            "created_at": datetime.utcnow().isoformat(),
            "last_used": None,
            "usage_count": 0,
            "active": True
        }
        
        self.redis.hset(f"api_key:{key_hash}", mapping=key_data)
        return key
    
    async def verify_api_key(self, api_key: str) -> dict:
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_data = self.redis.hgetall(f"api_key:{key_hash}")
        
        if not key_data or not key_data.get("active"):
            return None
        
        # Update usage statistics
        self.redis.hincrby(f"api_key:{key_hash}", "usage_count", 1)
        self.redis.hset(f"api_key:{key_hash}", "last_used", datetime.utcnow().isoformat())
        
        return key_data

# Dependency for API key authentication
async def verify_api_key_dependency(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
):
    api_key_handler = APIKeyHandler(redis_client)
    key_data = await api_key_handler.verify_api_key(credentials.credentials)
    
    if not key_data:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return key_data
```

#### Usage
```bash
# Generate API key (requires authentication)
curl -X POST "http://localhost:8000/api/v1/auth/api-keys" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Application"}'

# Response
{
  "api_key": "abc123def456...",
  "name": "My Application",
  "created_at": "2024-12-04T10:00:00Z"
}

# Use API key
curl -X GET "http://localhost:8000/api/v1/stocks/VCB" \
  -H "Authorization: Bearer abc123def456..."
```

### 3. OAuth 2.0 Integration

#### OAuth Configuration
```python
# services/api/src/auth/oauth_handler.py
from authlib.integrations.fastapi_oauth2 import OAuth2AuthorizationCodeBearer
from fastapi import Depends

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/auth",
    tokenUrl="https://oauth2.googleapis.com/token",
    scopes={"openid": "OpenID", "email": "Email", "profile": "Profile"}
)

class OAuthHandler:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
    
    async def verify_oauth_token(self, token: str):
        # Verify token with OAuth provider
        # Implementation depends on provider (Google, GitHub, etc.)
        pass
```

## Authorization & Permissions

### Role-Based Access Control (RBAC)
```python
# services/api/src/auth/permissions.py
from enum import Enum
from functools import wraps

class UserRole(Enum):
    ADMIN = "admin"
    PREMIUM = "premium"
    FREE = "free"
    READONLY = "readonly"

class Permission(Enum):
    READ_STOCKS = "read:stocks"
    READ_ANALYSIS = "read:analysis"
    READ_ALERTS = "read:alerts"
    WRITE_ALERTS = "write:alerts"
    ADMIN_USERS = "admin:users"

ROLE_PERMISSIONS = {
    UserRole.ADMIN: [Permission.READ_STOCKS, Permission.READ_ANALYSIS, 
                    Permission.READ_ALERTS, Permission.WRITE_ALERTS, Permission.ADMIN_USERS],
    UserRole.PREMIUM: [Permission.READ_STOCKS, Permission.READ_ANALYSIS, 
                      Permission.READ_ALERTS, Permission.WRITE_ALERTS],
    UserRole.FREE: [Permission.READ_STOCKS],
    UserRole.READONLY: [Permission.READ_STOCKS, Permission.READ_ANALYSIS]
}

def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: dict = Depends(get_current_user), **kwargs):
            user_role = UserRole(current_user.get("role", "free"))
            if permission not in ROLE_PERMISSIONS.get(user_role, []):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage in endpoints
@router.get("/stocks/{symbol}/analysis")
@require_permission(Permission.READ_ANALYSIS)
async def get_stock_analysis(symbol: str, current_user: dict = Depends(get_current_user)):
    # Implementation
    pass
```

### User Management
```python
# services/api/src/models/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.FREE

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
```

## Security Middleware

### Authentication Middleware
```python
# services/api/src/middleware/auth_middleware.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, jwt_handler, api_key_handler):
        super().__init__(app)
        self.jwt_handler = jwt_handler
        self.api_key_handler = api_key_handler
        
        # Public endpoints that don't require authentication
        self.public_paths = [
            "/health",
            "/docs",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        token = auth_header.split(" ")[1]
        
        # Try JWT authentication first
        user_data = self.jwt_handler.verify_token(token)
        if user_data:
            request.state.user = user_data
            return await call_next(request)
        
        # Try API key authentication
        key_data = await self.api_key_handler.verify_api_key(token)
        if key_data:
            request.state.user = {"user_id": key_data["user_id"], "auth_type": "api_key"}
            return await call_next(request)
        
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Security Best Practices

### Password Security
```python
# services/api/src/auth/password_handler.py
from passlib.context import CryptContext
import secrets
import string

class PasswordHandler:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_secure_password(self, length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def validate_password_strength(self, password: str) -> dict:
        issues = []
        
        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")
        
        return {"valid": len(issues) == 0, "issues": issues}
```

### Token Security
```python
# Token blacklisting for logout
class TokenBlacklist:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def blacklist_token(self, token: str, expires_at: datetime):
        # Store token hash with expiration
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        ttl = int((expires_at - datetime.utcnow()).total_seconds())
        self.redis.setex(f"blacklist:{token_hash}", ttl, "1")
    
    def is_blacklisted(self, token: str) -> bool:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return self.redis.exists(f"blacklist:{token_hash}")
```

## Configuration

### Environment Variables
```bash
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# API Key Configuration
API_KEY_HEADER=X-API-Key
API_KEY_PREFIX=sk_

# OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Security Settings
BCRYPT_ROUNDS=12
SESSION_TIMEOUT=3600
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION=900  # 15 minutes
```

### Security Headers
```python
# services/api/src/middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
```