from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from app.agent.router import route_query_async
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
    response = await route_query_async(request.message, user)
    return {"response": response}


@app.get("/traces")
async def traces(user=Depends(get_current_user)):
    if "admin" not in user["roles"]:
        raise HTTPException(status_code=403, detail="Admin only")
    return {"traces": get_traces()}


@app.get("/health")
async def health():
    return {"message": "Hello World"}


@app.delete("/clear_user_cache")
async def clear_user_cache(user=Depends(get_current_user)):
    return {"status": clear_conversation_history(user["username"])}
