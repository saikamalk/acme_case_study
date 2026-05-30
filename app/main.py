from fastapi import FastAPI, Depends
from pydantic import BaseModel

from app.agent.router import route_query
from app.auth.dependencies import get_current_user
from app.auth.rbac import require_role
from app.auth.user_context import current_user
from app.observability.logger import logger
from app.observability.middleware import LoggingMiddleware
from app.observability.trace_store import get_traces
from app.tools.customer_tools import get_customer_profile

app = FastAPI()
app.add_middleware(LoggingMiddleware)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/chat")
def chat(request: ChatRequest, user=Depends(get_current_user)):
    current_user.set(user)
    response = route_query(request.message, user)
    return {"response": response}


@app.get("/traces")
def traces():
    return {"traces": get_traces()}


@app.get("/customer/{customer_name}")
async def customer_profile(customer_name: str, user=Depends(get_current_user)):
    result = get_customer_profile(customer_name)
    if not result:
        return {"message": "customer not found"}
    return result


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/protected")
async def protected(user=Depends(get_current_user)):
    return {"message": "Authenticated user", "user": user}


@app.post("/admin-action")
async def admin_action(user=Depends(get_current_user)):
    require_role(user, ["admin"])
    return {"status": "allowed"}
