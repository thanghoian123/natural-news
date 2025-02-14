from datetime import datetime, timedelta
from enum import Enum
from random import choices
from string import digits
from typing import Any, Optional

from fastapi_mail import FastMail, MessageSchema, MessageType
from nltk import word_tokenize
from pydantic import BaseModel, computed_field, EmailStr
from sqlalchemy import Column, Integer, String
from sqlmodel import Field, Relationship, SQLModel

from vip_login.config import LOGGER, MAIL_CONFIG
from sqlalchemy import Boolean, DateTime, JSON, func

import uuid

def random_6_digits():
    return "".join(choices(digits, k=6))


class ChatMessage(SQLModel, table=True):

    __tablename__ = "chat_message"

    id: Optional[int] = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    is_llm: bool = False
    content: str = ""
    create_date: datetime = Field(default_factory=datetime.now)
    user_id: Optional[int] = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="messages")

    @computed_field
    @property
    def creator(self) -> str:
        if self.is_llm:
            return MessageCreator.model.value
        return MessageCreator.user.value
    
    @computed_field
    @property
    def token_count(self) -> int:
        tokens = word_tokenize(self.content)
        return len(tokens)

    @property
    def to_remove(self) -> bool:
        now = datetime.now() + timedelta(days=100)
        return now - self.create_date >= timedelta(days=90)


class Human(BaseModel):

    value: str = ""


class MessageCreator(str, Enum):
    user = "Human"
    model = "Assistant"


class Login(BaseModel):

    email: EmailStr = "test@email.com"
    session_password: str = ""


class SessionLogin(SQLModel, table=True):

    __tablename__ = "session_login"

    id: Optional[int] = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    email: str = Field(sa_column=Column("email", String, index=True, unique=True, nullable=False))
    session_password: str = Field(default_factory=random_6_digits, nullable=False)
    create_date: datetime = Field(default_factory=datetime.now, nullable=False)

    async def send_mail(self) -> None:
        html = (
            f"<p>Hi <b>{self.email}</b>,</p>"
            f"<p>This is your session login password:</p>"
            f"<h1><b>{self.session_password}</b></h1>"
        )
        message = MessageSchema(
            subject="HRS VIP Session Login Password",
            recipients=[self.email],
            body=html,
            subtype=MessageType.html,
        )
        try:
            fm = FastMail(config=MAIL_CONFIG)
            await fm.send_message(message=message)
            LOGGER.info(f"Session Password email sent to: {self.email}!")
        except Exception as e:
            LOGGER.error(f"Met an unexpected error while sending mail: {e.args}!")
        return None


class User(SQLModel, table=True):

    __tablename__ = "user"

    id: Optional[int] = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    login: str = Field(sa_column=Column("login", String, index=True, unique=True))
    token_allow: int = Field(nullable=True, default=100)
    messages: list[ChatMessage] = Relationship(back_populates="user")

    @computed_field
    @property
    def token_remain(self) -> int:
        now = datetime.now()
        year = now.year
        month = now.month
        this_month_messages = list(
            filter(
                lambda m: m.create_date.month == month and m.create_date.year == year,
                self.messages
            )
        )
        token_allow = self.token_allow if self.token_allow is not None else 0
        token_remain = token_allow - sum(
            list(
                map(
                    lambda m: m.token_count,
                    this_month_messages
                )
            )
        )
        return token_remain if token_remain >= 0 else 0

    def to_json(self) -> dict[str, Any]:
        return {
            "login": self.login,
            "token_remain": self.token_remain,
        }

class Customer(SQLModel, table=True):
    __tablename__ = "customer"

    # id: Optional[str] = Field(sa_column=Column("id", String, primary_key=True, index=True))
    loyaltylion_id: str = Field(sa_column=Column("loyaltylion_id", String, primary_key=True, unique=True, nullable=False))  # ID from LoyaltyLion
    merchant_id: Optional[str] = Field(sa_column=Column("merchant_id", String, nullable=True))
    email: Optional[str] = Field(sa_column=Column("email", String, unique=True, nullable=True))
    points_approved: int = Field(sa_column=Column("points_approved", Integer, default=0))
    points_pending: int = Field(sa_column=Column("points_pending", Integer, default=0))
    points_spent: int = Field(sa_column=Column("points_spent", Integer, default=0))
    points_balance: int = Field(sa_column=Column("points_balance", Integer, default=0))  # Total points balance
    rewards_claimed: int = Field(sa_column=Column("rewards_claimed", Integer, default=0))
    blocked: bool = Field(sa_column=Column("blocked", Boolean, default=False))
    enrolled_at: Optional[datetime] = Field(sa_column=Column("enrolled_at", DateTime, nullable=True))
    updated_at: datetime = Field(sa_column=Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))
    chat_tokens: int = Field(sa_column=Column("chat_tokens", Integer, default=0))
    
class WebhookEvent(SQLModel, table=True):
    __tablename__ = "webhookevent"

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), sa_column=Column("id", String, primary_key=True))  # Generating UUID automatically
    event_type: str = Field(sa_column=Column("event_type", String, nullable=False))  # example: "program_events/customer.points_earned"
    payload: dict = Field(sa_column=Column("payload", JSON, nullable=False))  # raw webhook data
    received_at: datetime = Field(sa_column=Column("received_at", DateTime(timezone=True), server_default=func.now()))