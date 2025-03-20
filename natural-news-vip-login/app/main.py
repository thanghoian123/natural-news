from fastapi import FastAPI
from app.database import engine, Base
from  app.api.routes.users import router as user_router
from app.api.routes.chats import router as chat_router
app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include User Router
app.include_router(user_router)
app.include_router(chat_router)
