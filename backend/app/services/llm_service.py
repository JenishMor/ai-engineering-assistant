from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import GEMINI_MODEL
from app.schemas.learning import LearningExplanation

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    # temperature=0.2,
)

def extract_text(content) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    return ""

async def generate_response(message: str) -> str:
    response = await llm.ainvoke(message)
    return extract_text(response.content)

async def stream_response(message: str):
    async for chunk in llm.astream(message):
        text = extract_text(chunk.content)
        if text:
            yield text

structured_llm = llm.with_structured_output(
    LearningExplanation,
    method="json_schema",
)

async def generate_learning_explanation(
    topic: str,
) -> LearningExplanation:
    return await structured_llm.ainvoke(
        f"""Explain the following software engineering topic for a
        developer learning AI engineering: {topic}.
        Provide concise key points and a practical next step."""
    )