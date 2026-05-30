from fastapi import FastAPI
from pydantic import BaseModel
from app.tools.customer_tools import get_customer_profile
from app.db.queries import get_issue_updates

app = FastAPI()


class ToolRequest(BaseModel):
    input: str


@app.get("/tools")
def list_tools():
    return {
        "tools": [
            {
                "name": "customer_profile_tool",
                "description": "Retrieve customer profile and open issues"
            },
            {
                "name": "issue_history_tool",
                "description": "Retrieve issue update history"
            }
        ]
    }


@app.post("/execute/customer_profile_tool")
def execute_customer_profile(request: ToolRequest):
    return get_customer_profile(request.input)


@app.post("/execute/issue_history_tool")
def execute_issue_history(request: ToolRequest):
    return get_issue_updates(int(request.input))
