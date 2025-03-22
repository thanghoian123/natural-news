from fastapi import FastAPI
from app.database import engine, Base
from  app.api.routes.users import router as user_router
from app.api.routes.chats import router as chat_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

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
