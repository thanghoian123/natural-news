from fastapi import APIRouter, Depends, HTTPException,Query,Request
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, LoginResponse
from app.services.user_service import create_user,get_user,login_user
from app.core.auth import verify_token
from fastapi.responses import JSONResponse


# Create User Router
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")
    users = db.query(User).filter(User.id == user_id).all()
    
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user_api(user_id: int, db: Session = Depends(get_db)):
    return get_user(db, user_id)

@router.post("", response_model=UserResponse)
def create_user_api(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

# @router.post("/login", response_model=UserResponse)
# def login_api(email: str, db: Session = Depends(get_db)):
#     return login_user(db, email)


@router.post("/login", response_model=LoginResponse)
def login_api(email: str = Query(...), db: Session = Depends(get_db)):
    return login_user(db, email)