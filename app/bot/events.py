import discord
import traceback
from discord.ext import commands
from app.core.config import settings
from app.utils.message_utils import (
    should_respond_to_message,
    process_message_attachments,
    construct_query,
    split_and_send_messages
)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        """Called when the bot has successfully connected to Discord."""
        print("----------------------------------------")
        print(f'Gemini Bot Logged in as {self.bot.user}')
        print("----------------------------------------")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Called when a message is sent in a channel the bot can see."""
        # Don't process commands as normal messages? 
        # Usually process_commands is called by on_message automatically if we don't override it,
        # OR if we override it, we must call await bot.process_commands(message).
        # However, since we're in a Cog listener, this runs *in addition* to the bot's on_message (if any).
        # But `commands.Bot` processes commands automatically.
        # We just need to make sure we don't block command processing if we want commands to work.
        # But here we are just reacting to messages.
        
        # Check if we should respond
        if not should_respond_to_message(message):
            return

        try:
            async with message.channel.typing():
                print(f"FROM: {message.author.name}: {message.content}")
                
                # Process attachments
                attachments, success = await process_message_attachments(message)
                if not success:
                    await message.channel.send("An error occurred while processing your attachments.")
                    return
                
                if message.attachments and len(attachments) == 0:
                    await message.channel.send("Attachments are of unsupported file types.")
                    return
                
                # Construct query
                query = await construct_query(message, attachments)
                
                # Generate response
                response_text = await self.bot.gemini_service.generate_response(
                    message.channel.id,
                    attachments,
                    query
                )
                
                # Send response
                await split_and_send_messages(message, response_text, settings.MAX_MESSAGE_LENGTH)
                
                # Save to persistent storage
                await self.bot.storage_service.save_chat_history(
                    message.channel.id,
                    self.bot.gemini_service.get_history(message.channel.id)
                )
                
        except Exception as e:
            print(f"Error: {e}")
            print(traceback.format_exc())
            
            # Handle specific error codes
            if hasattr(e, 'code') and getattr(e, 'code', None) == 50035:
                await message.channel.send("The message is too long for me to process.")
            else:
                await message.channel.send("An error occurred while processing your message.")

async def setup(bot):
    await bot.add_cog(Events(bot))
