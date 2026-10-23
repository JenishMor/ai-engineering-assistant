
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Create API
app = FastAPI(title="AI Engineering Assistant")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Define model
llm = ChatGoogleGenerativeAI(
    # model="gemini-3.8-flash",
    model="gemini-3.5-flash-lite",
    # temperature=0.2,
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def health_check():
    return {"status": "running"}

@app.post("/chat")
def chat(request: ChatRequest):
    # Invoke model
    response = llm.invoke(request.message)

    content = response.content
    if isinstance(content, list):
        content = "\n".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    return {"response": content}
