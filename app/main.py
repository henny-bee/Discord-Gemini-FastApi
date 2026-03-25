import asyncio
import contextlib
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import db
from app.bot.client import GeminiBot
from app.api.routes import router as api_router

# Initialize bot instance
bot = GeminiBot()

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI app.
    Handles startup and shutdown events.
    """
    # Startup
    try:
        # Connect to Database
        await db.connect()
        
        # Start Discord Bot in background
        # We use bot.start() instead of bot.run() because we're already in an async loop
        asyncio.create_task(bot.start(settings.DISCORD_BOT_TOKEN))
        
        print("FastAPI app started")
        yield
        
    except Exception as e:
        print(f"Error during startup: {e}")
        raise e
        
    finally:
        # Shutdown
        print("Shutting down...")
        try:
            if not bot.is_closed():
                await bot.close()
            db.close()
        except Exception as e:
            print(f"Error during shutdown: {e}")

app = FastAPI(title="Discord Gemini Chatbot API", lifespan=lifespan)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Discord Gemini Chatbot is running"}
