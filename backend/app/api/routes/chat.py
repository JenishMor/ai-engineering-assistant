import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import generate_response, stream_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    response = await generate_response(request.message)
    return ChatResponse(response=response)

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    async def events():
        try:
            async for text in stream_response(request.message):
                yield f"data: {json.dumps({'content': text})}\n\n"

            yield 'data: {"done": true}\n\n'

        except Exception:
            logger.exception("LLM streaming failed")
            yield f"data: {json.dumps({'error': 'Failed to generate response'})}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )