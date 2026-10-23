from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import GEMINI_MODEL
from app.schemas.learning import LearningExplanation

# Tool calling service
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from app.tools.utility_tools import calculate, get_current_utc_time

TOOLS = [calculate, get_current_utc_time]
TOOLS_BY_NAME = {tool.name: tool for tool in TOOLS}

llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    # temperature=0.2,
)

llm_with_tools = llm.bind_tools(TOOLS)

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

async def run_tool_assistant(message: str) -> str:
    messages = [
        SystemMessage(
            content=(
                "You are a helpful AI engineering assistant. "
                "Use the calculator for arithmetic and the time tool "
                "when the user asks for the current UTC time. "
                "Never invent tool results."
            )
        ),
        HumanMessage(content=message),
    ]

    for _ in range(5):
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)

        if not response.tool_calls:
            content = response.content

            if isinstance(content, str):
                return content

            if isinstance(content, list):
                return "".join(
                    item.get("text", "")
                    for item in content
                    if isinstance(item, dict)
                    and item.get("type") == "text"
                )

            return str(content)

        for tool_call in response.tool_calls:
            name = tool_call["name"]
            tool_instance = TOOLS_BY_NAME.get(name)

            if tool_instance is None:
                result = f"Unknown tool: {name}"
            else:
                try:
                    result = await tool_instance.ainvoke(tool_call["args"])
                except Exception:
                    result = "Tool execution failed."

            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                )
            )

    return "I couldn't complete the request within the tool-call limit."