import json
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import generate_response, stream_response

from app.schemas.learning import LearningExplanation
from app.services.llm_service import generate_learning_explanation

from app.services.llm_service import run_tool_assistant

from app.services.agent_graph import run_graph_assistant
from app.schemas.chat import ChatAgentResponse

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

@router.post("/structured", response_model=LearningExplanation)
async def structured_chat(request: ChatRequest):
    return await generate_learning_explanation(request.message)

@router.post("/agent", response_model=ChatAgentResponse)
async def chat_with_tools(request: ChatRequest):
    answer = await run_tool_assistant(request.message)
    return ChatAgentResponse(response=answer)

@router.post("/graph", response_model=ChatAgentResponse)
async def chat_with_graph(request: ChatRequest):
    answer = await run_graph_assistant(request.message)
    return ChatAgentResponse(response=answer)