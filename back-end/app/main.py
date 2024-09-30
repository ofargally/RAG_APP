from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os

from .database import fetch_conversations, store_conversations, remove_last_conversation
from .chat_agent import (
    create_vector_db,
    update_vector_db,
    stream_response
)
from .utils import recall

load_dotenv()

app = FastAPI()

# Configure CORS (optional since proxy is used)
origins = [
    "http://localhost:3000",  # Vite dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize vector DB on startup
@app.on_event("startup")
def startup_event():
    conversations = fetch_conversations()
    create_vector_db(conversations=conversations)

@app.post("/api/chat")
async def chat(prompt: str = Form(...), llm_api_key: str = Form(None)):
    try:
        stream_response(prompt=prompt, llm_api_key=llm_api_key)
        update_vector_db()
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})

@app.post("/api/forget")
async def forget():
    try:
        remove_last_conversation()
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})

@app.post("/api/recall")
async def recall_prompt(prompt: str = Form(...)):
    try:
        recall(prompt=prompt)
        stream_response(prompt=prompt)
        update_vector_db()
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)})

# Additional routes can be added as needed

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)