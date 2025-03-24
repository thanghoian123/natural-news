from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import TierEnum

# Define rewards per tier
TIER_REWARD_MAP = {
    TierEnum.BRONZE: 5,
    TierEnum.SILVER: 10,
    TierEnum.GOLD: 50,
    TierEnum.PLATINUM: float('inf'),  # Unlimited
}

def reset_rewards():
    """Reset user rewards based on their tier."""
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            user.reward = TIER_REWARD_MAP.get(user.tier, 5)  # Default to 5 if tier missing
        db.commit()
        print("✅ User rewards reset successfully!")
    except Exception as e:
        print(f"❌ Error resetting rewards: {e}")
    finally:
        db.close()

# Schedule the task every 24 hours
scheduler = BackgroundScheduler()
scheduler.add_job(reset_rewards, "interval", hours=24)
scheduler.start()
