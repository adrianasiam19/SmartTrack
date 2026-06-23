"""
AI Chat Router — endpoints for the learning assistant chatbot.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.users.models import User
from app.ai_chat.service import get_ai_response

router = APIRouter(tags=["AI Chat"])


class ChatRequest(BaseModel):
    message: str
    history: list[dict] | None = None
    lesson_context: str | None = None


class ChatResponse(BaseModel):
    response: str


@router.post("/ai/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, user: User = Depends(get_current_user)):
    """Send a message to the AI learning assistant."""
    if not body.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    message = body.message
    if body.lesson_context:
        message = f"[Context: I am studying {body.lesson_context}]\n\n{body.message}"

    response = await get_ai_response(message, body.history)
    return ChatResponse(response=response)