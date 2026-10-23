from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()

llm = ChatGoogleGenerativeAI(
    # model="gemini-3.6-flash"
    # model="gemini-3.8-flash",
    model="gemini-3.5-flash-lite",
    # temperature=0.2,
    # max_output_tokens=500,
)

console = Console()

response = llm.invoke(
    "Explain LangGraph with a simple example."
)

content = response.content

if isinstance(content, list):
    content = "\n".join(
        item["text"]
        for item in content
        if isinstance(item, dict) and item.get("type") == "text"
    )

console.print(Markdown(content))