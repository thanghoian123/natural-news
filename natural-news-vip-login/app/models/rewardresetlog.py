from sqlalchemy import Column, DateTime, Integer
from datetime import datetime
from app.database import Base
 
class RewardResetLog(Base):
    __tablename__ = "reward_reset_log"

    id = Column(Integer, primary_key=True, index=True)
    last_reset = Column(DateTime, default=datetime.utcnow)
