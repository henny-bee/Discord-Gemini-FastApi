from typing import List, Dict, Any, Optional
from app.core.database import db
from app.models.chat import Message

class StorageService:
    """Persistence layer for storing and retrieving conversation history."""

    async def insert_message(self, channel_id: int, message: Message) -> None:
        """
        Insert a new message into the history for a channel.
        
        Args:
            channel_id: Discord channel ID
            message: The message object to insert
        """
        await db.get_db().chat_history.update_one(
            {"channel_id": channel_id},
            {"$push": {"messages": message.model_dump()}},
            upsert=True
        )

    async def get_history(self, channel_id: int) -> List[Dict[str, Any]]:
        """
        Get the chat history for a channel.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            List of message dictionaries
        """
        try:
            doc = await db.get_db().chat_history.find_one({"channel_id": channel_id})
            if doc and "messages" in doc:
                return doc["messages"]
        except Exception as e:
            print(f"Error getting history: {e}")
        return []

    async def clear_history(self, channel_id: int) -> None:
        """
        Delete chat history for a specific channel.
        
        Args:
            channel_id: Discord channel ID
        """
        await db.get_db().chat_history.delete_one({"channel_id": channel_id})

    async def save_chat_history(self, channel_id: int, history: List[Dict[str, Any]]) -> None:
        """
        Save (overwrite) chat history for a specific channel.
        Legacy support for bulk saving.
        
        Args:
            channel_id: Discord channel ID
            history: List of message dictionaries
        """
        await db.get_db().chat_history.update_one(
            {"channel_id": channel_id},
            {"$set": {"messages": history}},
            upsert=True
        )

    async def load_chat_history(self) -> Dict[int, List[Dict[str, Any]]]:
        """
        Load chat history for ALL channels.
        Legacy support for startup loading.
        
        Returns:
            Dictionary mapping channel IDs to message lists
        """
        history = {}
        try:
            cursor = db.get_db().chat_history.find({})
            async for doc in cursor:
                if "channel_id" in doc:
                    history[doc["channel_id"]] = doc.get("messages", [])
        except Exception as e:
            print(f"Error loading chat history: {e}")
        return history

    async def save_tracked_threads(self, threads: List[int]) -> None:
        """
        Save list of tracked threads.
        
        Args:
            threads: List of thread IDs
        """
        await db.get_db().settings.update_one(
            {"key": "tracked_threads"},
            {"$set": {"value": threads}},
            upsert=True
        )

    async def load_tracked_threads(self) -> List[int]:
        """
        Load list of tracked threads.
        
        Returns:
            List of thread IDs
        """
        try:
            doc = await db.get_db().settings.find_one({"key": "tracked_threads"})
            if doc and "value" in doc:
                return doc["value"]
        except Exception as e:
            print(f"Error loading tracked threads: {e}")
        return []
        
    async def delete_chat_history(self, channel_id: int) -> None:
        """Alias for clear_history."""
        await self.clear_history(channel_id)
