from contextlib import asynccontextmanager
from os import getenv
from time import time
from typing import Annotated

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from jose import jwt
from sqlmodel import Session, SQLModel, create_engine, desc, select

from vip_login.config import *
from vip_login.schemas import *


SECRET = getenv("SECRET_KEY", SECRET_KEY)
DB_URL = getenv("DB_URL", DB)


async def _get_llm_response() -> str:
    return "1"


engine = create_engine(
    url=DB_URL,
    echo=True,
    connect_args={"check_same_thread": False},
)


def get_session():
    with Session(engine) as session:
        yield session


def monthly_clean_messages():
    with Session(engine) as session:
        statement = select(ChatMessage)
        messages = session.exec(statement)
        for msg in messages:
            if msg.to_remove:
                session.delete(msg)
        session.commit()


def create_all():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_all()
    background_task = BackgroundScheduler()
    cron = CronTrigger(hour=0)
    background_task.add_job(func=monthly_clean_messages, trigger=cron)
    background_task.start()
    yield
    background_task.shutdown()


app = FastAPI(lifespan=lifespan)


def decode_user_cookie(req: Request, session: Session = Depends(get_session)) -> User:
    error = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please login")
    cookie = req.cookies.get("natural-news-vip")
    if not cookie:
        raise error
    credentials = jwt.decode(
        cookie,
        key=SECRET,
        algorithms="HS512",
        audience="subscriber",
        issuer="NaturalNewsVip",
    )
    login = credentials.get("email")
    if not login:
        raise error
    statement = select(User).where(User.login == login).limit(1)
    user = session.exec(statement).one_or_none()
    if not user:
        raise error
    return user



@app.get("/login")
async def login() -> JSONResponse:
    return JSONResponse({"Hello": "World"})


@app.post("/login", response_model=User)
async def upsert_user(
    login: Login,
    session: Session = Depends(get_session)
) -> JSONResponse:
    TO_SEC_90_DAYS = 90 * 24 * 60 * 60
    user_statement = select(User).where(User.login == login.email).limit(1)
    user = session.exec(user_statement).one_or_none()
    if not user:
        user = User(login=login.email)
        session.add(user)
        session.commit()
        session.refresh(user)
    login_statement = select(SessionLogin).where(SessionLogin.email == login.email).limit(1)
    session_login = session.exec(login_statement).one_or_none()
    if not login.session_password:
        if not session_login:
            session_login = SessionLogin(email=login.email)
        else:
            session_login.session_password = uuid4()
        session.add(session_login)
        session.commit()
        session.refresh(session_login)
        await session_login.send_mail()

        return JSONResponse({"message": "Please check your email for session login password!"})
    else:
        if not session_login or session_login.session_password.__str__() != login.session_password:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Session Login and Password does not match!")
        ret_val = user.to_json()
        resp = JSONResponse(ret_val)
        exp = time() + TO_SEC_90_DAYS
        payload = dict(exp=exp, iss="NaturalNewsVip", aud="subscriber", email=login.email)
        token = jwt.encode(payload, key=SECRET, algorithm="HS512")
        resp.set_cookie(
            key="natural-news-vip",
            value=token,
            expires=exp,
        )
        return resp


@app.get("/")
async def get_root(
    user: Annotated[User, Depends(decode_user_cookie)],
) -> JSONResponse:
    resp = {"message": f"Hello {user.login}, you have {user.token_remain:,} token(s) left!"}
    return JSONResponse(resp)


@app.get("/chat")
async def get_chat(
    user: Annotated[User, Depends(decode_user_cookie)],
    session: Session = Depends(get_session),
) -> list[ChatMessage]:
    statement = select(ChatMessage).order_by(desc(ChatMessage.id)).where(ChatMessage.user_id == user.id).limit(10)
    messages = session.exec(statement)
    return messages


@app.post("/chat")
async def post_chat(
    user: Annotated[User, Depends(decode_user_cookie)],
    human: Human,
    session: Session = Depends(get_session),
) -> JSONResponse:
    if user.token_remain <= 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Your remaining token is exceeded!")
    human_message = ChatMessage(
        is_llm=False,
        content=human.value,
        user_id=user.id,
    )
    llm_response = await _get_llm_response()
    assistant_message = ChatMessage(
        is_llm=True,
        content=llm_response,
        user_id=user.id,
    )
    session.add_all([human_message, assistant_message])
    session.commit()
    resp = {
        "conversations": [
            {
                "from": "human",
                "value": human.value,
            },
            {
                "from": "assistant",
                "value": llm_response,
            }
        ]
    }
    return JSONResponse(resp)
    
