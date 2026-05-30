from typing import Optional, Literal

from pydantic import BaseModel


class CustomerResolutionResponse(BaseModel):
    customer_name: str


class ToolPlan(BaseModel):
    tool_name: Literal["customer_profile_tool", "issue_history_tool", "create_next_action_tool"]
    customer_name: Optional[str] = None
    issue_id: Optional[int] = None
    response_mode: Literal["standard", "escalation"]
    action_text: Optional[str] = None
