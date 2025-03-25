import jwt
import datetime
from fastapi import HTTPException, Security, Depends,Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import SECRET_KEY,ALGORITHM

# Secret key for signing tokens

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



# def verify_token(request: Request):
#     token = request.headers.get("Authorization")
#     if not token:
#         raise HTTPException(status_code=401, detail="Token missing")

#     try:
#         payload = jwt.decode(token.replace("Bearer ", ""), SECRET_KEY, algorithms=[ALGORITHM])
#         return payload  # Return decoded user information
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token expired")
#     except jwt.JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")
    
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
