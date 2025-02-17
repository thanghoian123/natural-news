from contextlib import asynccontextmanager
from os import getenv
from time import time
from typing import Annotated

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import Depends, FastAPI, Request, status, Header
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from jose import jwt
# from lorem import text
from sqlmodel import Session, SQLModel, create_engine, desc, select

from vip_login.config import *
from vip_login.schemas import *

from openai import OpenAI
import hmac
import hashlib
import json
import uuid

SECRET = getenv("SECRET_KEY", SECRET_KEY)
DB_URL = getenv("DB_URL", DB)
TOKEN_EQUIVALENT = getenv("TOKEN_EQUIVALENT", TOKEN_EQUIVALENT)
LOYALTY_WEBHOOK_SECRET = getenv("LOYALTY_WEBHOOK_SECRET", LOYALTY_WEBHOOK_SECRET)

def initialize_client_and_model(llm_selection):
    """Initialize the client and model based on the selected LLM engine."""
    if llm_selection == "Enoch-RC-14-128K":
        client = OpenAI(
            base_url="http://35.170.240.5:8081",
            api_key="aRMEhvlClTxqYosKSPrJ7BXCQQLrPy1Rf5e6SY2JMWgKgO1P0QaVUbOMCWvdWcDo"
        )
        model = 'LLaMA_CPP'
    return client, model

def verify_signature(request_body: bytes, received_signature: str):
    #Verify the webhook request using HMAC-SHA256
    computed_signature = hmac.new(
        key=LOYALTY_WEBHOOK_SECRET.encode(),
        msg=request_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_signature, received_signature)

async def _get_llm_response(request: ChatMessage) -> str:
    client, model = initialize_client_and_model("Enoch-RC-14-128K")

    # async def event_generator():
    #     # Create the stream
    #     stream = client.chat.completions.create(
    #         model=model,
    #         messages=[{"role": "user", "content": request.content}],
    #         stream=True,
    #     )

    #     try:
    #         async for chunk in stream:
    #             if len(chunk.choices) > 0 and chunk.choices[0].delta.content is not None:
    #                 # Extract the content from the chunk (assuming the structure you've shown)
    #                 content = chunk.choices[0].delta.content

    #                 if content:  # Only yield non-empty content
    #                     yield content  # Yield the content to the client

    #     except StopAsyncIteration:
    #         pass  # Stop iteration when the stream ends

    # return StreamingResponse(event_generator(), media_type="text/event-stream")

    not_stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": request.content}],
        stream=False,
    )
    print(not_stream)
    print(type(not_stream))
    choices = not_stream.choices
    if choices:
        response = choices[0].message.content
    else:
        response = 'No content available'
    total_tokens = not_stream.usage.total_tokens
    return response, total_tokens

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

if getenv("env", "DEV") == "DEV":
    allow_origins = ["http://localhost", "http://localhost:5173", "http://localhost:8000", "https://vip.healthrangerstore.com", "https://api-hrs.healthrangerstore.com"]
else:
    allow_origins = ["https://vip.healthrangerstore.com/"]
allow_origins = ["http://localhost", "http://localhost:5173", "http://localhost:8000", "https://vip.healthrangerstore.com", "https://api-hrs.healthrangerstore.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def decode_user_token(req: Request, session: Session = Depends(get_session)) -> User:
    error = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please login")
    authorization = req.headers.get("Authorization")
    
    if not authorization:
        raise error

    # Token format: "Bearer <token>"
    token_prefix = "Bearer "
    if not authorization.startswith(token_prefix):
        raise error
    
    token = authorization[len(token_prefix):]

    try:
        credentials = jwt.decode(
            token,
            key=SECRET,
            algorithms="HS512",
            audience="subscriber",
            issuer="HRSVip",
        )
    except jwt.JWTError:
        raise error

    login = credentials.get("email")
    if not login:
        raise error
    
    statement = select(User).where(User.login == login).limit(1)
    user = session.exec(statement).one_or_none()
    if not user:
        raise error
    
    return user


@app.get("/login")
async def login(
    user: Annotated[User, Depends(decode_user_token)],
) -> JSONResponse:
    ret_val = user.to_json()
    print(ret_val, "--------------------------------------")
    return JSONResponse(ret_val)

@app.post("/login")
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
            session_login.session_password = random_6_digits()
        session.add(session_login)
        session.commit()
        session.refresh(session_login)
        await session_login.send_mail()

        return JSONResponse({"message": "Please check your email for session login password!"})
    else:
        if not session_login or session_login.session_password != login.session_password:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Session Login and Password does not match!")
        ret_val = user.to_json()
        exp = time() + TO_SEC_90_DAYS
        payload = dict(exp=exp, iss="HRSVip", aud="subscriber", email=login.email)
        token = jwt.encode(payload, key=SECRET, algorithm="HS512")
        ret_val.update({"Authorization": f"Bearer {token}"})
        return JSONResponse(ret_val)


@app.get("/chat")
async def get_chat(
    user: Annotated[User, Depends(decode_user_token)],
    session: Session = Depends(get_session),
) -> list[ChatMessage]:
    statement = select(ChatMessage).order_by(desc(ChatMessage.id)).where(ChatMessage.user_id == user.id).limit(10)
    messages = session.exec(statement)
    return messages


@app.post("/chat")
async def post_chat(
    req: Request,
    user: Annotated[User, Depends(decode_user_token)],
    human: Human,
    session: Session = Depends(get_session),
) -> RedirectResponse:
    print(user, "====================================")
    # # Check if the user has enough tokens
    statement = select(Customer).where(Customer.email == user.login).limit(1)
    customer = session.exec(statement).one_or_none()

    print(customer, "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    
    if user.token_remain <= 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Your remaining token is exceeded!")



    # Proceed with sending the query and getting a response
    human_message = ChatMessage(
        is_llm=False,
        content=human.value,
        user_id=user.id,
    )
    llm_response, total_tokens = await _get_llm_response(human_message)
    # Calculate the token usage for the query (example: 1000 tokens for this example)
    token_usage = total_tokens  # Modify this based on the actual token usage

    user.token_allow -= token_usage
    # Deduct tokens
    session.commit()
    assistant_message = ChatMessage(
        is_llm=True,
        content=llm_response,
        user_id=user.id,
    )
    session.add_all([human_message, assistant_message])
    session.commit()

    return RedirectResponse(req.url_for("get_chat"), status_code=status.HTTP_303_SEE_OTHER)


@app.post("/webhook/loyaltylion")
async def loyaltylion_webhook(request: Request, session: Session = Depends(get_session)):
    # signature = request.headers.get("X-LoyaltyLion-Signature")
    # if not signature:
    #     raise HTTPException(status_code=400, detail="Missing Signature")
    
    body = await request.body()
    # if not verify_signature(body, signature):
    #     raise HTTPException(status_code=401, detail="Invalid signature")
    print(body)
    print(type(body))
    data = json.loads(body)
    event_type = data.get("topic")
    payload = data.get("payload", {})

    event = WebhookEvent(event_type=event_type, payload=payload)
    session.add(event)

    if event_type == "customer/update":
        customer_data = payload.get("customer", {})
        print("="*50)
        print(customer_data)
        print("="*50)
        loyaltylion_id = str(customer_data.get("id"))
        
        points_redeem = customer_data.get("rewards_claimed", 0)
        points_balance = points_redeem  # Assuming approved points are the current balance
        
        # Convert points to chat tokens (1 point = 10 chat tokens)
        chat_tokens = points_redeem * TOKEN_EQUIVALENT
        
        # Check if customer exists
        statement = select(Customer).where(Customer.loyaltylion_id == loyaltylion_id)
        customer = session.exec(statement).one_or_none()
        user_statement = select(User).where(User.email == customer_data.get("email"))
        user = session.exec(user_statement).one_or_none()
        if customer and user:
            # Update existing customer
            customer.points_approved = customer_data.get("points_approved", 0)
            customer.points_balance = points_balance
            customer.chat_tokens = chat_tokens  # Update chat tokens
            customer.rewards_claimed = customer_data.get("rewards_claimed", 0)
            customer.blocked = customer_data.get("blocked", False)
            customer.updated_at = customer_data.get("updated_at")

            # Update token
            user.token_allow += chat_tokens
            session.commit()
        else:
            # Create new customer
            customer = Customer(
                loyaltylion_id=loyaltylion_id,
                merchant_id=customer_data.get("merchant_id"),
                email=customer_data.get("email"),
                points_approved=customer_data.get("points_approved", 0),
                points_balance=points_balance,
                chat_tokens=chat_tokens,  # Set the chat tokens for the new customer
                rewards_claimed=customer_data.get("rewards_claimed", 0),
                blocked=customer_data.get("blocked", False),
                enrolled_at=customer_data.get("enrolled_at"),
                updated_at=customer_data.get("updated_at")
            )
            session.add(customer)

            # Create new user
            user = User(
                login=customer_data.get("email"),
                token_allow=chat_tokens
            )
            session.add(user)
            session.commit()

    return {"message": "Webhook received", "event_type": event_type}
