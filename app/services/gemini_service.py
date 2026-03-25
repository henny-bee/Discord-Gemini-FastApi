import traceback
from typing import Dict, List, Any, Optional

import google.generativeai as genai

from app.core.config import settings
from app.utils.logger import log_error

class GeminiService:
    """Manages interactions with Google's Generative AI API."""
    
    def __init__(self):
        """Initialize the AI service with configuration."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name="gemini-3-flash-preview",
            generation_config=settings.TEXT_GENERATION_CONFIG,
            safety_settings=settings.SAFETY_SETTINGS
        )
        self.message_history: Dict[int, Any] = {}
        
    def load_history(self, history_data: Dict[int, List[Dict[str, Any]]]) -> None:
        """
        Load previously saved chat history.
        
        Args:
            history_data: Dictionary mapping channel IDs to chat histories
        """
        for channel_id, history in history_data.items():
            # Convert stored dicts back to Gemini format
            # Stored format: [{'role': '...', 'content': '...', 'attachments': ...}]
            # Gemini format: [{'role': '...', 'parts': ['...']}]
            gemini_history = []
            for msg in history:
                role = msg.get('role')
                content = msg.get('content', '')
                # Note: We currently only restore text content as attachments 
                # might be expired URLs or blobs not stored in DB.
                if role and content:
                    gemini_history.append({
                        'role': role,
                        'parts': [content]
                    })
            
            try:
                self.message_history[channel_id] = self.model.start_chat(history=gemini_history)
            except Exception as e:
                print(f"Failed to load history for channel {channel_id}: {e}")
                self.message_history[channel_id] = self.model.start_chat(history=settings.BOT_TEMPLATE)
    
    async def generate_response(self, channel_id: int, attachments: List[Dict[str, Any]], text: str) -> str:
        """
        Generate a response from the AI model for the given input.
        
        Args:
            channel_id: Discord channel ID for context
            attachments: List of attachment data dictionaries (mime_type, data)
            text: The user's message text
            
        Returns:
            The AI model's response text
            
        Raises:
            Exception: If the API call fails
        """
        response: Optional[Any] = None
        try:
            # Prepare prompt parts
            prompt_parts: List[Any] = []
            for att in attachments:
                prompt_parts.append(att) # dict with mime_type, data
            prompt_parts.append(text)
            
            # Initialize chat session if not exists
            if channel_id not in self.message_history:
                self.message_history[channel_id] = self.model.start_chat(history=settings.BOT_TEMPLATE)
            
            # Send message to AI
            response = await self.message_history[channel_id].send_message_async(prompt_parts)
            return response.text if response else ""
            
        except Exception as e:
            # Log detailed error information for debugging
            history_info = "N/A"
            candidates = "N/A"
            parts = "N/A"
            prompt_feedbacks = "N/A"
            
            if channel_id in self.message_history:
                try:
                    history_info = str(self.message_history[channel_id].history)
                except:
                    pass
            
            if response:
                try:
                    candidates = str(response.candidates)
                    parts = str(response.parts)
                    prompt_feedbacks = str(response.prompt_feedbacks)
                except:
                    pass
            
            log_error(
                text=text,
                error_traceback=traceback.format_exc(),
                history=history_info,
                candidates=candidates,
                parts=parts,
                prompt_feedbacks=prompt_feedbacks
            )
            raise
    
    def reset_channel_history(self, channel_id: int, custom_template: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Reset the chat history for a channel.
        
        Args:
            channel_id: Discord channel ID
            custom_template: Optional custom initial template for the chat
        """
        if custom_template is None:
            custom_template = settings.BOT_TEMPLATE
        
        self.message_history[channel_id] = self.model.start_chat(history=custom_template)
    
    def delete_channel_history(self, channel_id: int) -> None:
        """
        Delete chat history for a channel.
        
        Args:
            channel_id: Discord channel ID
        """
        if channel_id in self.message_history:
            del self.message_history[channel_id]
    
    def get_history(self, channel_id: int) -> List[Dict[str, Any]]:
        """
        Get the chat history for a channel in a storage-friendly format.
        
        Args:
            channel_id: Discord channel ID
            
        Returns:
            The chat history list (List of message dicts)
        """
        if channel_id in self.message_history:
            # Convert Gemini history to storage format
            history = self.message_history[channel_id].history
            messages = []
            for content in history:
                text_content = ""
                for part in content.parts:
                    if hasattr(part, 'text'):
                        text_content += part.text
                
                messages.append({
                    "role": content.role,
                    "content": text_content,
                    # We don't store attachments in history for now as we don't have URLs here
                    "attachments": [],
                    "timestamp": None # We don't have original timestamp in Gemini history
                })
            return messages
        return []
