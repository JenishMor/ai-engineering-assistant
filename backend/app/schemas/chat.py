from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20_000)

class ChatResponse(BaseModel):
    response: str

class ChatAgentResponse(BaseModel):
    response: str

class GraphChatRequest(ChatRequest):
    thread_id: str = Field(min_length=1, max_length=100)