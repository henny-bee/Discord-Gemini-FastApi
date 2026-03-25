import discord
from discord import app_commands, Interaction, TextChannel
from discord.ext import commands
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.services.storage_service import StorageService

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='forget', description='Forget message history')
    @app_commands.describe(persona='Persona of bot')
    async def forget(self, interaction: Interaction, persona: Optional[str] = None):
        """
        Clear the conversation history for the current channel.
        Optionally set a new persona for the bot.
        """
        try:
            channel_id = interaction.channel_id
            if channel_id is None:
                await interaction.response.send_message("Error: Cannot determine channel.")
                return
            
            # Clear history in memory
            self.bot.gemini_service.delete_channel_history(channel_id)
            # Clear history in DB
            await self.bot.storage_service.delete_chat_history(channel_id)
            
            # Reset with new persona if provided
            if persona:
                temp_template = list(settings.BOT_TEMPLATE) # Copy
                temp_template.append({
                    'role': 'user',
                    'parts': [f"Forget what I said earlier! You are {persona}"]
                })
                temp_template.append({
                    'role': 'model',
                    'parts': ["Ok!"]
                })
                self.bot.gemini_service.reset_channel_history(channel_id, temp_template)
                
                # We should probably save the initial state to DB so it persists on restart?
                # The original code did: ChatDataManager.save_chat_history(channel_id, ai_service.get_history(channel_id))
                await self.bot.storage_service.save_chat_history(
                    channel_id, 
                    self.bot.gemini_service.get_history(channel_id)
                )
            
            await interaction.response.send_message("Message history for channel erased.")
            
        except Exception as e:
            print(f"Error in forget command: {e}")
            await interaction.response.send_message("An error occurred while processing your command.")
    
    @app_commands.command(
        name='createthread',
        description='Create a thread in which bot will respond to every message.'
    )
    @app_commands.describe(name='Thread name')
    async def create_thread(self, interaction: Interaction, name: str):
        """
        Create a new thread and add it to tracked threads.
        """
        try:
            channel = interaction.channel
            if channel is None:
                await interaction.response.send_message("Error: Cannot determine channel.")
                return
            
            if not isinstance(channel, TextChannel):
                await interaction.response.send_message("Error: Can only create threads in text channels.")
                return
            
            thread = await channel.create_thread(
                name=name,
                auto_archive_duration=60
            )
            thread_id = thread.id
            
            # Add to tracked threads
            if thread_id not in settings.TRACKED_CHANNELS:
                settings.TRACKED_CHANNELS.append(thread_id)
                # Save to DB
                await self.bot.storage_service.save_tracked_threads(settings.TRACKED_CHANNELS)
            
            await interaction.response.send_message(f"Thread {name} created!")
            
        except Exception as e:
            print(f"Error in createthread command: {e}")
            await interaction.response.send_message("Error creating thread!")

async def setup(bot):
    await bot.add_cog(Commands(bot))
