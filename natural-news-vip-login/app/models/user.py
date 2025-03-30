from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum, DateTime
from app.database import Base  # Ensure correct import
from app.schemas.user import PlatformEnum, TierEnum  # Import Enums only
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    type_platform = Column(SQLAlchemyEnum(PlatformEnum), nullable=False)
    tier = Column(SQLAlchemyEnum(TierEnum), nullable=False, default=TierEnum.BRONZE)  
    chats = relationship("Chat", back_populates="user")
    reward = Column(Integer, nullable=False, default=5)
    session_password = Column(String, nullable=True)  # Stores OTP
    session_password_expiry = Column(DateTime, nullable=True, default=lambda: datetime.utcnow() + timedelta(minutes=5))

    def __repr__(self):
        return f"User(id={self.id}, email={self.email}, tier={self.tier}, session_password={'SET' if self.session_password else 'None'})"
