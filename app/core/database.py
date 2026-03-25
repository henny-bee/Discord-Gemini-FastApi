from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class Database:
    client: AsyncIOMotorClient = None

    async def connect(self):
        """Establish connection to MongoDB."""
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        # Verify connection
        try:
            await self.client.admin.command('ping')
            print("Successfully connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise e

    def get_db(self):
        """Get the database instance."""
        if self.client is None:
            raise Exception("Database not initialized. Call connect() first.")
        return self.client[settings.DATABASE_NAME]

    def close(self):
        """Close the database connection."""
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

db = Database()
