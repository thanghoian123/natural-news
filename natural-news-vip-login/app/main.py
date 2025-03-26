from fastapi import FastAPI
from app.database import engine, Base
from  app.api.routes.users import router as user_router
from app.api.routes.chats import router as chat_router
from fastapi.middleware.cors import CORSMiddleware
from app.middlewares.token_middleware import TokenExpiryMiddleware
from app.daily_tasks import scheduler, reset_rewards

app = FastAPI()
app.add_middleware(TokenExpiryMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả nguồn gốc (dành cho testing)
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả HTTP methods (GET, POST, PUT, DELETE, v.v.)
    allow_headers=["*"],  # Cho phép tất cả headers
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include User Router
app.include_router(user_router)
app.include_router(chat_router)

@app.on_event("startup")
async def startup_event():
    reset_rewards()
    print("🚀 FastAPI started, APScheduler is running.")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print("🛑 APScheduler shutdown.")