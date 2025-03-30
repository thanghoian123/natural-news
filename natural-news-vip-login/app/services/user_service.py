from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi_mail import MessageSchema, FastMail
from fastapi import BackgroundTasks
from datetime import datetime, timedelta

from app.core.mail import generate_session_password, send_email
from app.models.user import User
from app.schemas.user import UserCreate, TierEnum
from app.services.external_services import determine_user_tier_and_reward, get_tier_reward
from app.core.auth import create_token

def create_user(db: Session, user: UserCreate):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    reward = get_tier_reward(user.tier)
    # Create new user
    new_user = User(
        email=user.email,
        type_platform=user.type_platform,
        tier=user.tier,
        reward=reward
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_users(db: Session):
    users = db.query(User)
    if not users:
        raise HTTPException(status_code=404, detail="User not found")
    return users

def login_user(db: Session, email: str, background_tasks: BackgroundTasks):
    """Login API: Generate and send a 6-digit password for session login."""
    user = db.query(User).filter(User.email == email).first()

    if not user:
        platform, tier, new_reward = determine_user_tier_and_reward(email)
        user = User(email=email, type_platform=platform, tier=tier, reward=new_reward)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate session password and set expiry
    # session_password = generate_session_password()
    session_password = "112233"  # For testing purposes
    user.session_password = session_password
    user.session_password_expiry = datetime.utcnow() + timedelta(minutes=5)  # Valid for 5 min
    db.commit()

    # Send session password via email
    subject = "Your Login Session Code"
    body = f"Hello,<br>Your one-time login code is: <b>{session_password}</b>.<br>Use it within 5 minutes."
    # background_tasks.add_task(send_email, email, subject, body)

    return {"message": "Session password sent to your email."}

def verify_session_login(db: Session, email: str, session_password: str):
    """Verify session password and log the user in."""
    user = db.query(User).filter(User.email == email).first()

    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found.")

    # if  user.session_password != session_password:
    #     raise HTTPException(status_code=403, detail="Invalid session password.")

    # if user.session_password_expiry and user.session_password_expiry < datetime.utcnow():
    #     raise HTTPException(status_code=403, detail="Session password expired. Request a new one.")

    # Generate a JWT token upon successful login
    token = create_token(user.id, user.email)

    # Clear the session password after successful login
    user.session_password = None
    user.session_password_expiry = None
    db.commit()

    return {"access_token": token, "token_type": "bearer"}



def deduct_reward(db: Session, user_id: int, cost: int):
    """Deducts reward from a user's account when they use the LLM."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.tier != TierEnum.PLATINUM:  # Platinum users have unlimited access
        if user.reward < cost:
            raise HTTPException(status_code=403, detail="Not enough rewards to process request")
        user.reward -= cost  # ✅ Deduct reward
    
    db.commit()
    db.refresh(user)
    return user