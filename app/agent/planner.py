from app.agent.exceptions import PlannerValidationError
from app.agent.llm import generate_plan
from app.agent.models import ToolPlan
from app.observability.logger import logger

AVAILABLE_TOOLS = [
    "customer_profile_tool",
    "issue_history_tool",
    "create_next_action_tool",
    "add_issue_update_tool",
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
    
    add_issue_update_tool:
    - add update to issue
    - append note to issue
    - record progress on issue
    - support_user and admin only
    - modifies issue history

    IMPORTANT:

    Use issue_history_tool ONLY when a specific issue identifier is referenced.
    Examples:
    
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
    
    "add update to issue 3 saying vendor confirmed root cause"
    -> add_issue_update_tool
    
    "record that issue 5 has been fixed"
    -> add_issue_update_tool
    
    "update issue 2 with not customer approved workaround"
    -> add_issue_update_tool
    
    "add note to issue 4 that engineering deploy hotfix:
    -> add_issue_update_tool
    
    "what is issue 5"
    -> issue_history_tool

    You must also determine the response_mode.
    
    response_mode = "standard" for:
    - customer lookups
    - customer profiles
    - open issues
    - issue history
    - issue timelines
    - issue updates
    - status retrieval
    - factual summaries
    - operational summaries
    - issue summaries
    - customer summaries
    
    response_mode = "escalation" ONLY when the user explicitly asks for:
    - risk assessment
    - severity assessment
    - executive summary
    - escalation analysis
    - customer situation analysis
    - management reporting
    - recommended next action
    - recommendation generation
    - missing information analysis
    
    IMPORTANT:
    
    The words:
    - summarize
    - summary
    - summarize issues
    - summarize open issues
    - summarize issue history
    
    DO NOT automatically imply escalation mode.
    
    Issue summaries and customer summaries should normally use:
    response_mode = "standard"
    
    Use escalation mode only when the user explicitly requests analysis, risk, recommendations, executive reporting, or escalation review.

    {feedback}

    Return ONLY a JSON object.
    
    IMPORTANT:
    Use issue_history_tool when the user is asking to VIEW, SHOW, DISPLAY, CHECK, GET or REVIEW issue history.
    Use add_issue_update_tool when the user is asking to ADD, UPDATE, RECORD, APPEND, SAVE or NOTE information on an issue.
    Use create_next_action_tool only when the user wants a future action to be created.

    Valid examples:
    {{
       "tool_name": "customer_profile_tool",
       "customer_name": "Globex",
       "response_mode": "standard"
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
    
    {{
        "tool_name": "add_issue_update_tool",
        "issue_id": 3
        "update_text": "Vendor confirmed root cause",
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
    elif plan.tool_name == "add_issue_update_tool":
        if not plan.issue_id or not plan.update_text:
            raise PlannerValidationError("issue_id and update_text are required for add_issue_update_tool")
    else:
        raise PlannerValidationError(f"Unsupported tool: {plan.tool_name}")


def create_plan(user_query: str):
    feedback = ""
    for attempt in range(1, MAX_PLANNER_RETRIES + 1):
        try:
            prompt = _build_prompt(user_query, feedback)
            plan = generate_plan(prompt)
            logger.info(f"Planner Attempt {attempt}")
            logger.info(f"Validating planner response: {plan}")
            _validate_plan(plan)
            logger.info(f"Planner response validated: {plan.model_dump()}")
            return plan
        except Exception as e:
            logger.error(f"Planner Attempt {attempt} Failed. ERROR:\n{str(e)}", exc_info=True)
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
