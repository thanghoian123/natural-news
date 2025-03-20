from sqlalchemy import Column, Integer, String, Enum
from app.database import Base  # Ensure correct import
from app.schemas.user import PlatformEnum, TierEnum  # Import Enums only
from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    type_platform = Column(SQLAlchemyEnum(PlatformEnum), nullable=False)
    tier = Column(SQLAlchemyEnum(TierEnum), nullable=False, default=TierEnum.BRONZE)  # ✅ Default value # ✅ Default value
    chats = relationship("Chat", back_populates="user")
