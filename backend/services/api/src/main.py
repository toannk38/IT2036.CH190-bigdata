from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import time
import asyncio
from datetime import datetime
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient

from .models import *
from .auth import AuthManager, User, UserRole
from .stock_api import router as stock_router
from .analysis_api import router as analysis_router
from ..config.settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="Stock AI API",
    description="Comprehensive stock analysis API with AI-powered insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Initialize components
auth_manager = AuthManager(settings.secret_key, settings.redis_url)
mongo_client = AsyncIOMotorClient(settings.mongodb_url)
db = mongo_client[settings.database_name]
redis_client = redis.from_url(settings.redis_url)

# Performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for health checks and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Get client IP
    client_ip = request.client.host
    
    # Check global rate limit (per IP)
    rate_key = f"rate_limit:ip:{client_ip}:{int(time.time() // 60)}"  # Per minute
    current_requests = await redis_client.get(rate_key)
    
    if current_requests and int(current_requests) > 1000:  # 1000 requests per minute per IP
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded", "message": "Too many requests from this IP"}
        )
    
    # Increment counter
    await redis_client.incr(rate_key)
    await redis_client.expire(rate_key, 60)
    
    return await call_next(request)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=f"HTTP_{exc.status_code}",
            message=exc.detail,
            timestamp=datetime.now()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details={"type": type(exc).__name__} if settings.debug else None,
            timestamp=datetime.now()
        ).dict()
    )

# Authentication endpoints
@app.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login with username and password"""
    # Simplified login - in production, verify against database
    if request.username == "admin" and request.password == "admin123":
        user = User(
            id="admin_user",
            username=request.username,
            email="admin@example.com",
            role=UserRole.ADMIN,
            created_at=datetime.now()
        )
    elif request.username == "user" and request.password == "user123":
        user = User(
            id="basic_user",
            username=request.username,
            email="user@example.com",
            role=UserRole.BASIC,
            created_at=datetime.now()
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = auth_manager.create_access_token(user)
    refresh_token = auth_manager.create_refresh_token(user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(auth_manager.access_token_expire.total_seconds())
    )

@app.post("/auth/register", response_model=UserResponse)
async def register(request: RegisterRequest):
    """Register new user"""
    # Check if user exists (simplified)
    existing_user = await db.users.find_one({"username": request.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create user
    hashed_password = auth_manager.hash_password(request.password)
    user_data = {
        "id": f"user_{int(time.time())}",
        "username": request.username,
        "email": request.email,
        "password": hashed_password,
        "role": UserRole.BASIC.value,
        "is_active": True,
        "created_at": datetime.now()
    }
    
    await db.users.insert_one(user_data)
    
    return UserResponse(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        role=user_data["role"],
        is_active=user_data["is_active"],
        created_at=user_data["created_at"],
        last_login=None
    )

@app.post("/auth/api-key")
async def generate_api_key(user: User = Depends(auth_manager.get_current_user)):
    """Generate API key for authenticated user"""
    api_key = auth_manager.generate_api_key(user.id)
    return {"api_key": api_key, "message": "API key generated successfully"}

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user(user: User = Depends(auth_manager.get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login
    )

@app.get("/auth/usage", response_model=APIUsageStats)
async def get_usage_stats(user: User = Depends(auth_manager.get_current_user)):
    """Get API usage statistics for current user"""
    now = datetime.now()
    hour_key = f"rate_limit:hour:{user.id}:{now.strftime('%Y%m%d%H')}"
    day_key = f"rate_limit:day:{user.id}:{now.strftime('%Y%m%d')}"
    
    hourly_count = await redis_client.get(hour_key) or 0
    daily_count = await redis_client.get(day_key) or 0
    
    limits = auth_manager.rate_limits[user.role]
    
    return APIUsageStats(
        user_id=user.id,
        requests_today=int(daily_count),
        requests_this_hour=int(hourly_count),
        daily_limit=limits["requests_per_day"],
        hourly_limit=limits["requests_per_hour"],
        remaining_daily=limits["requests_per_day"] - int(daily_count),
        remaining_hourly=limits["requests_per_hour"] - int(hourly_count)
    )

# Health check
@app.get("/health", response_model=HealthStatus)
async def health_check():
    """System health check"""
    start_time = time.time()
    
    # Check services
    services = {}
    
    # Check MongoDB
    try:
        await db.command("ping")
        services["mongodb"] = "healthy"
    except Exception:
        services["mongodb"] = "unhealthy"
    
    # Check Redis
    try:
        await redis_client.ping()
        services["redis"] = "healthy"
    except Exception:
        services["redis"] = "unhealthy"
    
    # Check external services
    import aiohttp
    async with aiohttp.ClientSession() as session:
        # AI Analysis Service
        try:
            async with session.get(f"{settings.ai_analysis_url}/health", timeout=5) as response:
                services["ai_analysis"] = "healthy" if response.status == 200 else "unhealthy"
        except:
            services["ai_analysis"] = "unhealthy"
        
        # LLM Analysis Service
        try:
            async with session.get(f"{settings.llm_analysis_url}/health", timeout=5) as response:
                services["llm_analysis"] = "healthy" if response.status == 200 else "unhealthy"
        except:
            services["llm_analysis"] = "unhealthy"
        
        # Aggregation Service
        try:
            async with session.get(f"{settings.aggregation_url}/health", timeout=5) as response:
                services["aggregation"] = "healthy" if response.status == 200 else "unhealthy"
        except:
            services["aggregation"] = "unhealthy"
    
    # Performance metrics
    response_time = time.time() - start_time
    
    # Overall status
    overall_status = "healthy" if all(s == "healthy" for s in services.values()) else "degraded"
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.now(),
        version=settings.service_version,
        uptime=time.time() - settings.start_time,
        services=services,
        performance={
            "response_time": response_time,
            "memory_usage": 0,  # Would implement actual memory monitoring
            "cpu_usage": 0      # Would implement actual CPU monitoring
        }
    )

# Include routers
app.include_router(stock_router)
app.include_router(analysis_router)

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    
    try:
        # Forward to aggregation service WebSocket
        import websockets
        async with websockets.connect(f"ws://localhost:8005/ws") as aggregation_ws:
            # Relay messages between client and aggregation service
            async def client_to_aggregation():
                async for message in websocket.iter_text():
                    await aggregation_ws.send(message)
            
            async def aggregation_to_client():
                async for message in aggregation_ws:
                    await websocket.send_text(message)
            
            await asyncio.gather(
                client_to_aggregation(),
                aggregation_to_client()
            )
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    settings.start_time = time.time()
    print(f"Stock AI API started at {datetime.now()}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    mongo_client.close()
    await redis_client.close()
    print("Stock AI API shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )