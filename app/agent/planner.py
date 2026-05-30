import json

from app.agent.exceptions import PlannerValidationError
from app.agent.llm import generate_response, generate_plan
from app.agent.models import ToolPlan
from app.observability.logger import logger

AVAILABLE_TOOLS = [
    "customer_profile_tool",
    "issue_history_tool",
    "create_next_action_tool"
]
MAX_PLANNER_RETRIES = 3


def _build_prompt(user_query: str, feedback: str = ""):
    return f"""
    You are an enterprise tool planner.

    User Query:
    {user_query}

    Available Tools:
    {AVAILABLE_TOOLS}

    Tool Descriptions:

    customer_profile_tool:
    - customer information
    - customer profile
    - open issues
    - customer health
    - company status
    - escalation review
    - question about customers

    issue_history_tool:
    - issue history
    - issue updates
    - issue timeline
    - issue progress
    
    create_next_action_tool:
    - create next action
    - save next action
    - persist recommendation
    - admin only

    IMPORTANT:

    Use issue_history_tool ONLY when the query contains a specific issue id.
    Examples:
    "show issues"
    -> issue_history_tool
    
    "show history for issue 5"
    -> issue_history_tool

    "show updates for issue 3"
    -> issue_history_tool

    "what is happening with globex"
    -> customer_profile_tool

    "how bad is initech situation"
    -> customer_profile_tool

    "show open issues for globex"
    -> customer_profile_tool
    
    "create next action for issue 10"
    -> create_next_action_tool

    You must also determine the response mode.

    response_mode values:

    standard
    - customer lookup
    - issue lookup
    - status retrieval
    - factual responses

    escalation
    - risk assessment
    - customer health
    - executive summary
    - severity analysis
    - recommendations
    - management reporting

    {feedback}

    Return ONLY a JSON object.

    Valid examples:
    {{
       "tool_name": "customer_profile_tool",
       "customer_name": "Globex",
       "response_mode": "standard
    }}

    {{
       "tool_name": "customer_profile_tool",
       "customer_name": "Initech",
       "response_mode": "escalation"
    }}

    {{
        "tool_name": "issue_history_tool",
        "issue_id": 1,
        "response_mode": "standard"
    }}
    
    {{
        "tool_name": "create_next_action_tool",
        "issue_id": 1,
        "action_text": "Escalate to infrastructure team within 24 hours",
        "response_mode": "standard"
    }}
    
    Every response MUST contain:
    - tool_name
    - response_mode
    
    Do not omit fields.
    """


def _validate_plan(plan: ToolPlan):
    if plan.tool_name == "customer_profile_tool":
        if not plan.customer_name:
            raise PlannerValidationError("customer_name is required for customer_profile_tool")
    elif plan.tool_name == "issue_history_tool":
        if not plan.issue_id:
            raise PlannerValidationError("issue_id is required for issue_history_tool")
    elif plan.tool_name == "create_next_action_tool":
        if not plan.issue_id or not plan.action_text:
            raise PlannerValidationError("issue_id and action_text are required for create_next_action_tool")
    else:
        raise PlannerValidationError(f"Unsupported tool: {plan.tool_name}")


def create_plan(user_query: str):
    feedback = ""
    for attempt in range(1, MAX_PLANNER_RETRIES + 1):
        try:
            prompt = _build_prompt(user_query, feedback)
            plan = generate_plan(prompt)
            logger.info(f"PLANNER_ATTEMPT={attempt}")
            logger.info(f"PLANNER_RAW_RESPONSE={plan}")
            _validate_plan(plan)
            logger.info(f"PLAN_DUMP={plan.model_dump()}")
            return plan
        except Exception as e:
            logger.error(f"PLANNER_ATTEMPT_FAILED={attempt}; ERROR={str(e)}")
            feedback = f"""
            PREVIOUS ATTEMPT FAILED.
            Validation Error:
            {str(e)}
            Requirements:
            1. Return ONLY JSON
            2. Do not include explanations
            3. Populate all required fields
            4. Ensure tool arguments are valid
            """
            if attempt == MAX_PLANNER_RETRIES:
                raise PlannerValidationError(f"Planner failed after {MAX_PLANNER_RETRIES} attempts")
    return None
