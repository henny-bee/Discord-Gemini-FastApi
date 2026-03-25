"""
Handles incoming Discord messages and orchestrates message processing.
"""
import traceback
from discord import Message, DMChannel
from typing import List, Dict, Optional, Any
from app.utils.attachments import get_attachment_data
from app.core.config import settings


async def construct_query(message: Message, attachments: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Construct the query string from a Discord message.
    
    Args:
        message: The Discord message
        attachments: Processed attachment data
        
    Returns:
        The formatted query string
    """
    author_name = message.author.name
    
    # Build base query
    if not message.attachments:
        query = f"@{author_name} said \"{message.clean_content}\""
    else:
        if not message.content:
            query = f"@{author_name} sent attachments:"
        else:
            query = f"@{author_name} said \"{message.clean_content}\" while sending attachments:"
    
    # Add quoted message context if replying
    if message.reference is not None and message.reference.message_id:
        try:
            reply_message = await message.channel.fetch_message(message.reference.message_id)
            # Only add if not replying to the bot itself
            if reply_message.author.id != (message.guild.me.id if message.guild and message.guild.me else 0):
                query = f"{query} while quoting @{reply_message.author.name} \"{reply_message.clean_content}\""
                
                # Include attachments from quoted message
                if reply_message.attachments and attachments is not None:
                    reply_attachments = await get_attachment_data(reply_message.attachments)
                    if reply_attachments:
                        attachments.extend(reply_attachments)
        except Exception:
            pass # Ignore if fetch fails
    
    return query


async def process_message_attachments(message: Message) -> tuple[List[Dict[str, Any]], bool]:
    """
    Process attachments from a message.
    
    Args:
        message: The Discord message
        
    Returns:
        Tuple of (attachments_list, success_flag)
    """
    if not message.attachments:
        return [], True
    
    attachments = await get_attachment_data(message.attachments)
    
    if attachments is None:
        return [], False
    
    if len(attachments) == 0:
        return [], True  # No supported attachments, but no error
    
    return attachments, True


def should_respond_to_message(message: Message) -> bool:
    """
    Determine if the bot should respond to a message.
    
    Args:
        message: The Discord message
        
    Returns:
        True if bot should respond
    """
    # Don't respond to own messages
    if message.author.bot: # Generally ignore all bots, or at least itself
        return False
        
    if message.guild and message.guild.me and message.author == message.guild.me:
        return False
    
    # Don't respond to @everyone mentions
    if message.mention_everyone:
        return False
    
    # Check if bot is mentioned, it's a DM, or channel is tracked
    bot_user = message.guild.me if message.guild else None
    bot_mentioned = bot_user and bot_user.mentioned_in(message) if bot_user else False
    is_dm = isinstance(message.channel, DMChannel)
    in_tracked_channel = message.channel.id in settings.TRACKED_CHANNELS
    # Threads are also in tracked list (handled by same list)
    
    return bot_mentioned or is_dm or in_tracked_channel


async def split_and_send_messages(message: Message, text: str, max_length: int) -> None:
    """
    Split a long message into chunks and send them as replies.
    
    Args:
        message: The original Discord message to reply to
        text: The text to send
        max_length: Maximum length of each chunk
    """
    messages = []
    if not text:
        return

    for i in range(0, len(text), max_length):
        sub_message = text[i:i + max_length]
        messages.append(sub_message)
    
    # Send each part as a separate reply
    current_message = message
    for string in messages:
        current_message = await current_message.reply(string)
