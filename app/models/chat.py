from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class Attachment(BaseModel):
    url: str
    filename: str
    type: str

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    attachments: List[Attachment] = Field(default_factory=list)

class ChatHistory(BaseModel):
    channel_id: int
    messages: List[Message] = Field(default_factory=list)
