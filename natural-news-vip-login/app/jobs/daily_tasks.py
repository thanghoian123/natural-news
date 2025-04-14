from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.jobs.scheduler import scheduler  # ✅ Import shared scheduler

from app.models.user import User
from app.models.rewardresetlog import RewardResetLog  # Import the new model
from app.schemas.user import TierEnum

TIER_REWARD_MAP = {
    TierEnum.BRONZE: 5,
    TierEnum.SILVER: 10,
    TierEnum.GOLD: 50,
    TierEnum.PLATINUM: 99999,
}

RESET_INTERVAL_HOURS = 24  # Ensure rewards reset every 24 hours

def reset_rewards():
    """Reset user rewards based on their tier, ensuring no duplicate resets."""
    db: Session = SessionLocal()
    try:
        # Get last reset time
        last_reset_entry = db.query(RewardResetLog).order_by(RewardResetLog.last_reset.desc()).first()
        last_reset_time = last_reset_entry.last_reset if last_reset_entry else None

        now = datetime.utcnow()
        if last_reset_time and (now - last_reset_time) < timedelta(hours=RESET_INTERVAL_HOURS):
            print("⏳ Rewards already reset recently. Skipping...")
            return  # Skip reset if within 24 hours
        
        # Reset user rewards
        users = db.query(User).all()
        for user in users:
            user.reward = TIER_REWARD_MAP.get(user.tier, 5)
        db.commit()

        # Update last reset time
        db.add(RewardResetLog(last_reset=now))
        db.commit()

        print("✅ User rewards reset successfully!")

    except Exception as e:
        print(f"❌ Error resetting rewards: {e}")
    finally:
        db.close()

# Schedule the task every 24 hours
scheduler.add_job(reset_rewards, "interval", hours=24)  # Change to hours=24