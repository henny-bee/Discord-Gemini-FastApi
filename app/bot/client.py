import discord
from discord.ext import commands
from app.core.config import settings
from app.services.gemini_service import GeminiService
from app.services.storage_service import StorageService

class GeminiBot(commands.Bot):
    """
    Custom Bot class for Gemini Chatbot.
    Inherits from commands.Bot to support extensions and commands.
    """
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=settings.BOT_PREFIX,
            intents=intents,
            help_command=None,
            activity=discord.Game(settings.BOT_ACTIVITY)
        )
        
        self.gemini_service = GeminiService()
        self.storage_service = StorageService()
        
    async def setup_hook(self):
        """
        Called when the bot is starting up.
        Used to load extensions and sync commands.
        """
        # Load extensions
        await self.load_extension("app.bot.events")
        await self.load_extension("app.bot.commands")
        
        # Load persisted data
        try:
            history_data = await self.storage_service.load_chat_history()
            self.gemini_service.load_history(history_data)
            
            # Load tracked threads if needed (handled in config/settings usually, but stored in DB)
            tracked_threads = await self.storage_service.load_tracked_threads()
            # Update settings with tracked threads from DB
            settings.TRACKED_CHANNELS.extend(tracked_threads)
            
        except Exception as e:
            print(f"Error loading persisted data: {e}")

        # Sync commands with Discord
        # Note: In production, sync specific guild or global. Global takes up to an hour.
        # For dev/testing, it's often better to sync to a specific guild, but here we'll sync global.
        try:
             await self.tree.sync()
             print("Commands synced globally.")
        except Exception as e:
             print(f"Error syncing commands: {e}")
