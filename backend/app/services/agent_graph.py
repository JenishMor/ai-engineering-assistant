
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from app.services.llm_service import llm, TOOLS

llm_with_tools = llm.bind_tools(TOOLS)

async def call_model(state: MessagesState):
    response = await llm_with_tools.ainvoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(MessagesState)

builder.add_node("llm", call_model)
builder.add_node("tools", ToolNode(TOOLS))

builder.add_edge(START, "llm")

builder.add_conditional_edges(
    "llm",
    tools_condition,
    {
        "tools": "tools",
        END: END,
    },
)

builder.add_edge("tools", "llm")

# Development-only persistence; survives requests, not process restarts.
checkpointer = InMemorySaver()
agent_graph = builder.compile(checkpointer=checkpointer)

async def run_graph_assistant(message: str, thread_id: str) -> str:
    result = await agent_graph.ainvoke(
        {"messages": [HumanMessage(content=message)]},
        config={"configurable": {"thread_id": thread_id}},
    )

    content = result["messages"][-1].content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    return str(content)
