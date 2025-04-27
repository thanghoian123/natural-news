from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, LoginResponse
from app.services.user_service import create_user, get_user, login_user, verify_session_login
from app.services.external_services import get_customer_total_spent,update_tier_customer,get_customer_by_email
from app.core.auth import verify_token
from fastapi.responses import JSONResponse
import json


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

@router.get("/shopify/user/{email}")
async def get_shopify_user(email: str):
    return get_customer_by_email(email)

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


@router.post("/webhook/shopify/order_update")
async def order_update_webhook(request: Request, db: Session = Depends(get_db)):
    """Handles Shopify order updates for payment, refunds, and cancellations."""
    payload = await request.json()
    print("Received payload:", json.dumps(payload, indent=2))

    financial_status = payload.get("financial_status")

    # Track only relevant financial statuses
    if financial_status not in ["paid", "refunded", "partially_refunded"]:
        return {"message": "No significant status change to track."}

    customer = payload.get("customer", {})
    customer_id = customer.get("id")
    customer_email = customer.get("email")
    # If no customer data, return early
    if not customer_id:
        print("Warning: No customer data found in the payload.")
        return {"message": "No customer information available, skipping update."}
    total_spent = get_customer_total_spent(customer_id)
    # Update customer tier if necessary
    update_tier_customer(customer_email, total_spent, db)

    print("Updated customer spending:", {
        "customer_id": customer_id,
        "customer_email": customer_email,
        "total_spent": total_spent,
    })

    return {
        "customer_id": customer_id,
        "customer_email": customer_email,
        "total_spent": total_spent,
    }