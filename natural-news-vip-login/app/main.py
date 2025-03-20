from fastapi import FastAPI
from app.database import engine, Base
from  app.api.routes.users import router as user_router

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Include User Router
app.include_router(user_router)
