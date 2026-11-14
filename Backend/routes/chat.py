"""
BhashaVerse - Chat & AI RAG Routes
Provides endpoint for conversational cultural search and proverbs grounding.
"""

from fastapi import APIRouter
from Backend.schemas import ChatRequest, ChatResponse
from Backend.utils.chatbot_utils import generate_chat_response

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Generate an AI response grounded in the verified Indian proverbs corpus.
    Supports Ollama, Gemini, Groq, OpenAI, and Native Offline Corpus Engine.
    """
    response_text = generate_chat_response(
        query=request.query,
        language_filter=request.language_filter,
        engine_choice=request.engine_choice or "Auto-Detect",
        custom_api_key=request.custom_api_key,
    )

    return ChatResponse(
        response=response_text,
        query=request.query,
        language_filter=request.language_filter,
        engine_used=request.engine_choice or "Auto-Detect",
    )
