# backend/app/main.py

import logging
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import os

from .database import fetch_conversations, store_conversations, remove_last_conversation
from .chat_agent import create_vector_db, update_vector_db, stream_response
from .utils import recall

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # Vite dev server
    "http://localhost",       # Additional origins if needed
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
    logger.info("Initializing vector DB...")
    conversations = fetch_conversations()
    create_vector_db(conversations=conversations)
    logger.info("Vector DB initialized.")

@app.post("/api/chat")
async def chat(prompt: str = Form(...), llm_api_key: str = Form(None)):
    logger.info(f"Received /api/chat request with prompt: {prompt}")
    try:
        #response_text = stream_response(prompt=prompt, llm_api_key=llm_api_key)
        response_text = "This is a static assistant response."
        update_vector_db()
        logger.info("Successfully generated assistant response.")
        return JSONResponse(content={"status": "success", "response": response_text})
    except Exception as e:
        logger.error(f"Error in /api/chat: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)})

@app.post("/api/forget")
async def forget():
    logger.info("Received /api/forget request.")
    try:
        remove_last_conversation()
        logger.info("Successfully forgot last conversation.")
        return JSONResponse(content={"status": "success"})
    except Exception as e:
        logger.error(f"Error in /api/forget: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)})

@app.post("/api/recall")
async def recall_prompt(prompt: str = Form(...)):
    logger.info(f"Received /api/recall request with prompt: {prompt}")
    try:
        recall(prompt=prompt)
        #response_text = stream_response(prompt=prompt)
        response_text = "This is a static assistant response."
        update_vector_db()
        logger.info("Successfully recalled and generated assistant response.")
        return JSONResponse(content={"status": "success", "response": response_text})
    except Exception as e:
        logger.error(f"Error in /api/recall: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)})

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
