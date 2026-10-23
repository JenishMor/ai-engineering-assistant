from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router

# Initialize API
app = FastAPI(title="AI Engineering Assistant")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Health check endpoint
@app.get("/")
async def health_check():
    return {"status": "running"}

app.include_router(chat_router)