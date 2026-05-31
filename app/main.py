from fastapi import FastAPI, Depends
from pydantic import BaseModel

from app.agent.router import route_query
from app.auth.dependencies import get_current_user
from app.auth.user_context import current_user
from app.cache.memory import clear_conversation_history
from app.observability.middleware import LoggingMiddleware
from app.observability.trace_store import get_traces

app = FastAPI()
app.add_middleware(LoggingMiddleware)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/chat")
async def chat(request: ChatRequest, user=Depends(get_current_user)):
    current_user.set(user)
    response = route_query(request.message, user)
    return {"response": response}


@app.get("/traces")
async def traces():
    return {"traces": get_traces()}


@app.get("/health")
async def root():
    return {"message": "Hello World"}


@app.delete("/clear_user_cache")
async def clear_user_cache(username: str):
    return {"status": clear_conversation_history(username)}
