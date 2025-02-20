from datetime import datetime, timedelta
from enum import Enum
from random import choices
from string import digits
from typing import Any, Optional

from fastapi_mail import FastMail, MessageSchema, MessageType
# from nltk import word_tokenize
import tiktoken

from pydantic import BaseModel, computed_field, EmailStr
from sqlalchemy import Column, Integer, String
from sqlmodel import Field, Relationship, SQLModel, Session, select

from vip_login.config import LOGGER, MAIL_CONFIG
from sqlalchemy import Boolean, DateTime, JSON, func

import uuid
from uuid import UUID, uuid4
from urllib.parse import quote_plus
from dataclasses import dataclass
import requests


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
    # def token_count(self) -> int:
    #     tokens = word_tokenize(self.content)
    #     return len(tokens)
    
    def token_count(self) -> int:
        """Prints a comparison of three string encodings."""
        encoding = tiktoken.get_encoding("o200k_base")
        token_integers = encoding.encode(self.content)
        num_tokens = len(token_integers)
        return num_tokens

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
    token_allow: int = Field(nullable=True, default=0)
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

    customer_id: Optional[int] = Field(sa_column=Column("customer_id", Integer, primary_key=True, autoincrement=True))  # Assuming customer_id is a unique identifier for each customer
    reward_id: Optional[int] = Field(sa_column=Column("reward_id", Integer, nullable=True))
    customer_email: Optional[str] = Field(sa_column=Column("customer_email", String, unique=True, nullable=True))
    reward_identifier: Optional[str] = Field(sa_column=Column("reward_identifier", String, nullable=True))
    customer_merchant_id: Optional[str] = Field(sa_column=Column("customer_merchant_id", String, nullable=True))
    reward_fulfilment_id: Optional[int] = Field(sa_column=Column("reward_fulfilment_id", Integer, nullable=True))
    
    updated_at: datetime = Field(sa_column=Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now()))
    chat_tokens: int = Field(sa_column=Column("chat_tokens", Integer, default=0))

#######-----------Brighton-----------#######
@dataclass
class BrighteonPagination:

    page: int = 1
    pages: int = 1
    count: int = 0

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> "BrighteonPagination":
        return cls(
            page = json_data["page"],
            pages = json_data["pages"],
            count = json_data["count"],
        )


@dataclass
class BrighteonVideoAnalytics:

    video_view: int = 0

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> "BrighteonVideoAnalytics":
        video_view = json_data.get("videoView", 0)
        if not isinstance(video_view, int):
            video_view = int(video_view)
        return cls(video_view =video_view)


@dataclass
class BrighteonVideo:

    analytics: Optional[BrighteonVideoAnalytics] = None
    channel_avatar: str = ""
    duration: int = 0
    brighteon_id: str = ""
    brighteon_channel_id: str = ""
    name: str = ""
    create_at: Optional[datetime] = None
    thumbnail: str = ""

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> "BrighteonVideo":
        return cls(
            analytics = BrighteonVideoAnalytics.from_json(json_data["analytics"]),
            brighteon_channel_id = json_data["channelId"],
            brighteon_id = json_data["id"],
            channel_avatar = json_data["channelAvatar"],
            create_at = datetime.fromisoformat(json_data["createdAt"]),
            duration = int(json_data["durationMS"] / 1000),
            name = json_data["name"],
            thumbnail = json_data["thumbnail"],
        )


@dataclass
class BrighteonVideoPageResponse:
    
    videos: list[BrighteonVideo] = Field(default_factory=list)
    pagination: Optional[BrighteonPagination] = 0
    videos_count: int = 0

    @classmethod
    def from_json(cls, json_data: dict[str, Any]):
        videos = []
        for data in json_data["videos"]:
            videos.append(BrighteonVideo.from_json(data))
        return cls(
            videos = videos,
            pagination = BrighteonPagination.from_json(json_data["pagination"]),
            videos_count = json_data["videosCount"],
        )
    
class KeywordVideoRel(SQLModel, table=True):

    __tablename__ = "keyword_video_rel"

    keyword_id: Optional[int] = Field(foreign_key="video_keyword.id", primary_key=True)
    video_id: Optional[UUID] = Field(foreign_key="video.id", primary_key=True)

class VideoCreator(SQLModel, table=True):

    __tablename__ = "video_creator"

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True, nullable=False, index=True)
    name: str = Field(index=True, nullable=False, unique=True)
    brighteon_id: str = ""
    followers_count: int = 0
    avatar_url: str = ""
    videos: list["Video"] = Relationship(back_populates="creator")

    @property
    def brighteon_base_url(self) -> str:
        return "https://www.brighteon.com/"

    @property
    def brighteon_base_api_v3_url(self) -> str:
        return f"{self.brighteon_base_url}api-v3/"

    @property
    def brighteon_channels_videos_path(self) -> str:
        return f"channels/{quote_plus(self.name.lower())}/videos"

    @property
    def get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
        }

    @property
    def get_all_videos_params(self) -> dict[str, int | str]:
        return {
            "uploaded": "all",
            "duration": "all",
            "quality": "all",
            "sort": "index",
            "videosType": "BROWSE",
            "selectedRange": "All",
        }

    @computed_field
    @property
    def videos_count(self) -> int:
        return len(self.videos)

    def __repr__(self) -> str:
        return (
            f"VideoCreator(\n"
            f"  id={self.id},\n"
            f"  name={self.name},\n"
            f"  brighteon_base_url={self.brighteon_base_url},\n"
            f")"
        )

    def __str__(self) -> str:
        return f"VideoCreator(name={self.name})"

    def pull(self, session: Session, page: int = 1) -> None:
        param = self.get_all_videos_params
        param.update({"page": page})
        response_data = None
        try:
            api_v3_home_full_path = self.brighteon_base_api_v3_url + self.brighteon_channels_videos_path
            resp = requests.get(
                url=api_v3_home_full_path,
                params=param,
                headers=self.get_headers,
            )
            resp.raise_for_status()
            response_data = resp.json()
            resp_model = BrighteonVideoPageResponse.from_json(response_data)
            with session:
                for video in resp_model.videos:
                    if not self.brighteon_id or not self.avatar_url:
                        self.brighteon_id = video.brighteon_channel_id
                        self.avatar_url = video.channel_avatar
                        session.add(self)
                    statement = select(Video).where(Video.brighteon_id == video.brighteon_id).limit(1)
                    db_video = session.exec(statement).one_or_none()
                    if db_video:
                        continue
                    db_video = Video(
                        brighteon_id=video.brighteon_id,
                        title=video.name,
                        duration=video.duration,
                        creator_id=self.id,
                        create_date=video.create_at,
                        thumbnail=video.thumbnail,
                        analytics=video.analytics.__dict__,
                    )
                    session.add(db_video)
                session.commit()
            if page < resp_model.pagination.pages:
                page += 1
                self.pull(session=session, page=page)
        except Exception as e:
            LOGGER.error(e.args)
            if response_data is not None:
                LOGGER.info(response_data)

class VideoKeyword(SQLModel, table=True):

    __tablename__ = "video_keyword"

    id: int = Field(sa_column=Column("id", Integer, primary_key=True, autoincrement=True, index=True, unique=True))
    name: str = Field(nullable=False, index=True, unique=True)


class Video(SQLModel, table=True):

    __tablename__ = "video"

    id: UUID = Field(default_factory=uuid4, nullable=False, unique=True, index=True, primary_key=True)
    brighteon_id: str = Field(unique=True, nullable=False, index=True)
    title: str = ""
    duration: int = 0
    thumbnail: str = ""
    creator_id: Optional[UUID] = Field(foreign_key="video_creator.id")
    creator: Optional[VideoCreator] = Relationship(back_populates="videos")
    description: str = ""
    keywords: list[VideoKeyword] = Relationship(link_model=KeywordVideoRel)
    analytics: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    create_date: Optional[datetime] = None

    @computed_field
    @property
    def brighteon_url(self) -> str:
        return f"https://www.brighteon.com/{self.brighteon_id}"

    @property
    def duration_str(self) -> str:
        return str(timedelta(seconds=self.duration)).lstrip("0:")

    @property
    def age(self) -> str:
        delta = datetime.now() - self.create_date
        if delta.days >= 30:
            return f"{delta.days // 30} month(s) ago"
        if delta.days > 0:
            return f"{delta.days} day(s) ago"
        if delta.seconds >= 3_600:
            return f"{delta.seconds // 3_600} hour(s) ago"
        else:
            return f"{delta.seconds // 60} minute(s) ago"

    def to_json(self) -> dict[str, Any]:
        name = self.title.lstrip("BrightLearn - ")
        if len(name) > 55:
            name = name[:52] + "..."
        return {
            "url": self.brighteon_url,
            "embed_url": self.brighteon_id,
            "age": self.age,
            "duration": self.duration_str,
            "name": name,
            "thumbnail": self.thumbnail,
            "analytics": self.analytics,
            "creator": {
                "name": self.creator.name,
                "avatar": self.creator.avatar_url,
            }
        }