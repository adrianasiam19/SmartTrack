"""
revision/router.py — WASSCE Revision Hub API endpoints
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.users.models import User
from app.revision.service import generate_topic_content, ask_ai_question

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/revision", tags=["WASSCE Revision"])


class GenerateTopicRequest(BaseModel):
    topic: str


class AskAIRequest(BaseModel):
    topic: str
    question: str
    history: Optional[list[dict]] = None


class GenerateTopicResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    source: Optional[str] = None


class AskAIResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None


@router.post("/generate-topic", response_model=GenerateTopicResponse)
async def generate_topic(
    body: GenerateTopicRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate comprehensive WASSCE revision content for a topic.

    The AI generates explanations, worked examples, practice questions,
    common mistakes, exam tips, and more for SHS 3 revision.
    """
    if not body.topic.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic cannot be empty.",
        )

    try:
        content = await generate_topic_content(body.topic.strip())
        source = content.pop("_source", "ai")
        return GenerateTopicResponse(
            success=True,
            data=content,
            source=source,
        )
    except Exception as e:
        logger.error(f"Failed to generate topic '{body.topic}': {e}")
        return GenerateTopicResponse(
            success=False,
            error=f"Failed to generate content: {str(e)}",
        )


@router.post("/ask", response_model=AskAIResponse)
async def ask_ai(
    body: AskAIRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Ask a follow-up question about a specific revision topic.

    The AI uses the topic as context to provide relevant answers.
    """
    if not body.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    if not body.topic.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic cannot be empty.",
        )

    try:
        response = await ask_ai_question(
            topic=body.topic.strip(),
            question=body.question.strip(),
            history=body.history,
        )
        return AskAIResponse(success=True, response=response)
    except Exception as e:
        logger.error(f"Failed to answer question: {e}")
        return AskAIResponse(
            success=False,
            error=f"Failed to get AI response: {str(e)}",
        )
