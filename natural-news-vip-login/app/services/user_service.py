from sqlalchemy.orm import Session
from fastapi import HTTPException
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

def login_user(db: Session, email: str):
    """Login API: Check email in ActiveCampaign/Shopify and update DB if found."""
    
    # platform, tier, new_reward = determine_user_tier_and_reward(email)

    platform = "SHOPIFY"
    tier = "SILVER"
    new_reward = get_tier_reward(tier)
    # Check if user already exists in DB
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Create new user if not in DB
        user = User(email=email, type_platform=platform, tier=tier, reward=new_reward)
        db.add(user)
    else:
        # Update existing user
        user.type_platform = platform
        user.tier = tier  # ✅ Update tier based on platform response
        # Only update reward if it's lower than the new tier's minimum
        if user.reward < new_reward:
            user.reward = new_reward


    db.commit()
    db.refresh(user)

    # Generate JWT Token
    token = create_token(user.id, user.email)

    return {"access_token": token, "token_type": "bearer"}

# def get_customer_id(email):
#     response = requests.get(f'{ACTIVE_CAMPAIGN_URL}/customers', headers=headers)
#     customers = response.json().get('customers', [])
#     for customer in customers:
#         if customer.get('email') == email:
#             return customer.get('id')
#     return None

# def get_customer_info(email):
#     customer_id = get_customer_id(email)
#     """Retrieve customer details from ActiveCampaign E-Commerce API."""
#     url = f"{ACTIVE_CAMPAIGN_URL}/ecomCustomers/{customer_id}"
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         customer_data = response.json().get("ecomCustomer", {})
#         return customer_data
#     else:
#         return None  # Handle customer not found case

# def get_total_spent(customer_id):
#     """Extract and return the total amount spent by the customer."""
#     customer_info = get_customer_info(customer_id)
    
#     if not customer_info:
#         return f"Customer ID {customer_id} not found."

#     total_spent = float(customer_info.get("total_spent", 0))  # Extract total spent
#     return total_spent



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