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
from datetime import datetime

# from agents import AnalyzingAgent, InputAgent
from vip_login.utils import normalize_result
from vip_login.workflows import get_good_workflow, get_bad_workflow
from pathlib import Path
import os


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
    user: Annotated[User, Depends(decode_user_token)],  # Decoding user token to get user info
    session: Session = Depends(get_session)  # Getting the database session
) -> JSONResponse:
    # Query the Customer table to get the customer data by user email
    statement = select(Customer).where(Customer.customer_email == user.login).limit(1)
    customer = session.exec(statement).one_or_none()

    # Prepare the return value based on user info
    ret_val = user.to_json()
    if customer:
        # If customer exists, update token_allow with chat_tokens from Customer
        ret_val["token_allow"] = customer.chat_tokens
    else:

        customer = Customer(
            customer_email=login.email,
            chat_tokens=0,  # Set the chat tokens for the new customer
            updated_at=datetime.utcnow()
        )
        ret_val["token_allow"] = 0
        session.add(customer)
        session.commit()
        session.refresh(customer)
        # Handle the case where no customer is found with the email
        LOGGER.warning(f"Customer with email {user.login} not found.")

    # Log the return value for debugging purposes
    return JSONResponse(ret_val)

@app.post("/login")
async def upsert_user(
    login: Login,
    session: Session = Depends(get_session)
) -> JSONResponse:
    print(login, "========Login+++++++++++")
    TO_SEC_90_DAYS = 90 * 24 * 60 * 60
    user_statement = select(User).where(User.login == login.email).limit(1)
    user = session.exec(user_statement).one_or_none()
    customer_statement = select(Customer).where(Customer.customer_email == login.email).limit(1)
    customer = session.exec(customer_statement).one_or_none()
    
    # if not customer:
    #     customer = Customer(
    #         customer_email=login.email,
    #         chat_tokens=0,  # Set the chat tokens for the new customer
    #         updated_at=datetime.utcnow()
    #     )
    #     print("=====not-customer=====================",customer)

    #     session.add(customer)
    #     session.commit()
    #     session.refresh(customer)
    
    # if not user:

    #     user = User(login=login.email, token_allow=0)
    #     print("=====not-user=====================",user)

    #     session.add(user)
    #     session.commit()
    #     session.refresh(user)
    # Ensure user token_allow matches customer chat_tokens
    # if user.token_allow != customer.chat_tokens:
    #     print("==========================")
    #     print(user.token_allow)
    #     print(customer.chat_tokens)
    #     print("=====================")
    #     user.token_allow = customer.chat_tokens
    #     session.commit()
    #     session.refresh(user)

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
        ret_val["token_allow"] = customer.chat_tokens
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
    # # Check if the user has enough tokens
    statement = select(Customer).where(Customer.customer_email == user.login).limit(1)
    customer = session.exec(statement).one_or_none()
    
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

    customer.chat_tokens -= token_usage
    # Deduct tokens
    session.commit()
    assistant_message = ChatMessage(
        is_llm=True,
        content=llm_response,
        user_id=user.id,
    )
    session.add_all([human_message, assistant_message])
    session.commit()

    return RedirectResponse("/chat", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/webhook/loyaltylion")
async def loyaltylion_webhook(request: Request, session: Session = Depends(get_session)):
    body = await request.body()
    print(body)
    print(type(body))
    data = json.loads(body)
    
    # Get data from webhook
    customer_id = data.get("customer_id")
    reward_id = data.get("reward_id")
    customer_email = data.get("customer_email")
    reward_identifier = data.get("reward_identifier")
    customer_merchant_id = data.get("customer_merchant_id")
    reward_fulfilment_id = data.get("reward_fulfilment_id")

    if reward_id == 204296:
        points_redeem = 10000
        chat_tokens = points_redeem * TOKEN_EQUIVALENT
    else:
        chat_tokens = 0
    
    # Query DB
    statement = select(Customer).where(Customer.customer_email == customer_email).limit(1)
    customer = session.exec(statement).one_or_none()
    user_statement = select(User).where(User.login == customer_email).limit(1)
    user = session.exec(user_statement).one_or_none()

    if customer and user:
        customer.customer_id = customer_id
        customer.reward_id = reward_id
        customer.reward_identifier = reward_identifier
        customer.customer_merchant_id = customer_merchant_id
        customer.reward_fulfilment_id = reward_fulfilment_id
        customer.chat_tokens += chat_tokens
        customer.updated_at = datetime.utcnow()

        # Update token
        user.token_allow += chat_tokens
    else:
        # Create new customer
        customer = Customer(
            reward_id=reward_id,
            customer_email=customer_email,
            customer_id=customer_id,
            reward_identifier=reward_identifier,
            customer_merchant_id=customer_merchant_id,
            reward_fulfilment_id=reward_fulfilment_id,
            chat_tokens=chat_tokens,  # Set the chat tokens for the new customer
            updated_at=datetime.utcnow()
        )
        session.add(customer)

        # Create new user
        user = User(
            login=customer_email,
            token_allow=chat_tokens
        )
        session.add(user)

    try:
        session.commit()
    except Exception as e:
        session.rollback()  # Rollback transaction in case of error
        print(f"Error during commit: {e}")
        raise HTTPException(status_code=500, detail="Database error")

    return {"message": "Webhook received", "event_type": f"User {customer_email} exchanged points"}



class Workflow:
    def __init__(self, agents):
        self.agents = agents
 
    def run(self, input_data):
        current_data = input_data
        current_status = f""
        for agent in self.agents:
            agent.perceive(current_data)
            current_data = agent.act()
            if agent.name == "AnalyzingAgent":
                analyzer_result = current_data
                main_analyser_result = analyzer_result.split(" ")[0]
            elif agent.name != "InputAgent":
                current_status += f"\n\n{current_data}"

        return current_status if current_status != "" else analyzer_result


@app.post("/ingredient-chat")
async def post_chat(
    req: Request,
    user: Annotated[User, Depends(decode_user_token)],
    human: Human,
    session: Session = Depends(get_session),
) -> RedirectResponse:
    # # Check if the user has enough tokens
    statement = select(Customer).where(Customer.customer_email == user.login).limit(1)
    customer = session.exec(statement).one_or_none()
    
    if user.token_remain <= 0:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Your remaining token is exceeded!")
    
    # Proceed with sending the query and getting a response
    human_message = ChatMessage(
        is_llm=False,
        content=human.value,
        user_id=user.id,
    )
    good_workflow_agents = get_good_workflow(human_message.content)
    analysis_workflow = Workflow(good_workflow_agents)
    # elif normalize_result(characteristic) == "bad":
    #     bad_workflow_agents = get_bad_workflow(topic)
    #     analysis_workflow = Workflow(bad_workflow_agents)

    llm_response, total_tokens = analysis_workflow.run(human_message.content)
    # Calculate the token usage for the query (example: 1000 tokens for this example)
    token_usage = total_tokens  # Modify this based on the actual token usage

    customer.chat_tokens -= token_usage
    # Deduct tokens
    session.commit()
    assistant_message = ChatMessage(
        is_llm=True,
        content=llm_response,
        user_id=user.id,
    )
    session.add_all([human_message, assistant_message])
    session.commit()

    return RedirectResponse("/ingredient-chat", status_code=status.HTTP_303_SEE_OTHER)