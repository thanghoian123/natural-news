import jwt
import datetime
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Secret key for signing tokens
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 60  # Token expiry time

# Security scheme for authorization
security = HTTPBearer()


def create_token(user_id: int, email: str):
    """Generate a JWT token with user info."""
    expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expiry
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Middleware to verify token validity."""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Returns user info if valid
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
