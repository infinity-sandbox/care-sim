from typing import Optional, List
from pydantic import BaseModel, Field

class GetQueryPayload(BaseModel):
    query: str
    userId: str
    sessionId: str

class GetRegeneratePayload(BaseModel):
    query: str
    userId: str
    sessionId: str
    messageId: str

class GetReactionPayload(BaseModel):
    userId: str
    sessionId: str
    messageId: str
    rating: str
    feedbackText: str
