from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.api.routes.users import router as user_router
from app.api.routes.chats import router as chat_router
from app.middlewares.token_middleware import TokenExpiryMiddleware
from app.jobs.daily_tasks import  reset_rewards
from app.jobs.scheduler import  scheduler
from app.jobs.crawler import  start_crawler_task


# Initialize FastAPI app
def create_app() -> FastAPI:
    app = FastAPI()

    # Middleware
    configure_middlewares(app)

    # Routers
    configure_routers(app)

    # Database
    initialize_database()

    # Events
    configure_events(app)

    return app

def configure_middlewares(app: FastAPI):
    """Configure middlewares for the FastAPI app."""
    app.add_middleware(TokenExpiryMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (for testing purposes)
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )

def configure_routers(app: FastAPI):
    """Include API routers."""
    app.include_router(user_router)
    app.include_router(chat_router)

def initialize_database():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)

def configure_events(app: FastAPI):
    """Configure startup and shutdown events."""
    @app.on_event("startup")
    async def startup_event():
        reset_rewards()
        # start_crawler_task()
        scheduler.start()
        print("🚀 FastAPI started, APScheduler is running.")

    @app.on_event("shutdown")
    async def shutdown_event():
        scheduler.shutdown()
        print("🛑 APScheduler shutdown.")

# Create the app instance
app = create_app()