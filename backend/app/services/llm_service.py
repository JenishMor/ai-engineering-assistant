from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import GEMINI_MODEL

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