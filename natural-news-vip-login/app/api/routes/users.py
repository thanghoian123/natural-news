from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, LoginResponse
from app.services.user_service import create_user, get_user, login_user, verify_session_login
from app.services.external_services import get_customer_total_spent,update_tier_customer
from app.core.auth import verify_token
from fastapi.responses import JSONResponse


# Create User Router
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
# def get_users(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
def get_users(db: Session = Depends(get_db), payload: dict = Depends(verify_token)):

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found in token")
    users = db.query(User).filter(User.id == user_id).all()
    
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users

@router.get("/{user_id}", response_model=UserResponse)
# def get_user_api(user_id: int, db: Session = Depends(get_db)):
def get_user_api(user_id: int, db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    return get_user(db, user_id)

@router.post("", response_model=UserResponse)
def create_user_api(user: UserCreate, db: Session = Depends(get_db), payload: dict = Depends(verify_token)):
    return create_user(db, user)

@router.post("/login")
def login_api(
    background_tasks: BackgroundTasks,  # ✅ Move this first
    email: str = Query(...), 
    db: Session = Depends(get_db)  
):
    return login_user(db, email, background_tasks)

@router.post("/verify-login", response_model=LoginResponse)
def verify_login_api(
    email: str = Query(...), 
    session_password: str = Query(...), 
    db: Session = Depends(get_db)
):
    """Step 2: Verify session password and return a JWT token if valid."""
    return verify_session_login(db, email, session_password)

@router.post("/webhook/shopify/order_paid")
async def order_paid_webhook(request: Request,  db: Session = Depends(get_db)):
    """Trigger when an order is paid."""
    payload = await request.json()
    customer_id = payload.get("customer", {}).get("id")

    if not customer_id:
        raise HTTPException(status_code=400, detail="Invalid order data")

    total_spent = get_customer_total_spent(customer_id)
    if total_spent is None:
        raise HTTPException(status_code=500, detail="Failed to fetch customer spending")

    if total_spent > 3000:
        update_tier_customer(customer_id, total_spent,db)

    return {"customer_id": customer_id, "total_spent_last_3_months": total_spent}

@router.post("/webhook/shopify/order_cancelled")
async def order_cancelled_webhook(request: Request,  db: Session = Depends(get_db)):
    """Trigger when an order is canceled."""
    payload = await request.json()
    customer_email = payload.get("customer", {}).get("email")

    if not customer_email:
        raise HTTPException(status_code=400, detail="Invalid order data")

    total_spent = get_customer_total_spent(customer_email)
    if total_spent is None:
        raise HTTPException(status_code=500, detail="Failed to fetch customer spending")

    if total_spent < 3000:
        update_tier_customer(customer_email,total_spent,db)

    return {"customer_email": customer_email, "total_spent_last_3_months": total_spent}