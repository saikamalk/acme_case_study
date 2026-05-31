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
        - customer situation
        - escalation review
        - customer analysis
        - operational summaries
        - customer summaries
        - executive reviews
        - questions about customers
    issue_history_tool:
        - issue history
        - issue updates
        - issue timeline
        - issue progress
        - issue details
        - issue investigation
    create_next_action_tool:
        - create next action
        - save next action
        - record next action
        - persist recommendation
        - persist follow-up action
        - create future action
        - admin only
    
    IMPORTANT:
    This tool is ONLY for creating and storing a next action.
    
    DO NOT use create_next_action_tool for:
        - risk assessments
        - executive summaries
        - escalation reviews
        - customer situation analysis
        - severity analysis
        - recommendation generation
        - "what should we do next"
        - "how bad is this situation"
    Those requests should use customer_profile_tool with response_mode="escalation".
    
    add_issue_update_tool:
        - add update to issue
        - append note to issue
        - record progress on issue
        - record issue update
        - support_user and admin only
        - modifies issue history
    
    IMPORTANT TOOL SELECTION RULES
    
    Use issue_history_tool ONLY when a specific issue identifier is referenced.
    
    Examples:
    
    "show history for issue 5"
    -> issue_history_tool

    "show updates for issue 3"
    -> issue_history_tool

    "what is issue 5"
    -> issue_history_tool
    
    "review issue 10"
    -> issue_history_tool
    ------------------------------------------------------
    Use customer_profile_tool for customer-level requests.
    
    Examples:
    
    "what is happening with globex"
    -> customer_profile_tool

    "show open issues for globex"
    -> customer_profile_tool
    
    "show customer status for initech"
    -> customer_profile_tool
    
    "summarize globex"
    -> customer_profile_tool
    
    "summarize open issues for initech"
    -> customer_profile_tool
    
    "how bad is initech situation"
    -> customer_profile_tool

    "give executive summary for globex"
    -> customer_profile_tool
    
    Use create_next_action_tool ONLY when the user explicitly wants a next action to be CREATED, SAVED, RECORDED, or PERSISTED.
    
    Examples:
    
    "create next action for issue 10"
    -> create_next_action_tool
    
    "save a follow-up action for issue 3"
    -> create_next_action_tool
    
    "record next step for issue 5"
    -> create_next_action_tool
    ------------------------------------------------------
    Use add_issue_update_tool ONLY when the user wants to modify issue history.
    
    Examples:
    
    "add update to issue 3 saying vendor confirmed root cause"
    -> add_issue_update_tool
    
    "record that issue 5 has been fixed"
    -> add_issue_update_tool
    
    "update issue 2 with note customer approved workaround"
    -> add_issue_update_tool
    
    "add note to issue 4 that engineering deployed hotfix"
    -> add_issue_update_tool
    ------------------------------------------------------

    You must also determine response_mode.
    response_mode = "standard" for:
        - customer lookups
        - customer profiles
        - open issues
        - issue history
        - issue timelines
        - issue updates
        - factual summaries
        - operational summaries
        - issue summaries
        - customer summaries
        - status retrieval
    response_mode = "escalation" ONLY when the user explicitly requests:
        - risk assessment
        - severity assessment
        - executive summary
        - escalation analysis
        - customer situation analysis
        - management reporting
        - recommendation generation
        - recommended next action analysis
        - missing information analysis
    IMPORTANT:
    The words:
        - summarize
        - summary
        - summarize issues
        - summarize open issues
        - summarize issue history
    
    DO NOT automatically imply escalation mode.
    
    Issue summaries and customer summaries normally use:
    response_mode = "standard"
    ------------------------------------------------------
    ESCALATION EXAMPLES
    
    User:
    "How bad is the Initech situation?"
    
    Output:
    {{
    "tool_name": "customer_profile_tool",
    "customer_name": "Initech",
    "response_mode": "escalation"
    }}
    
    User:
    "Give me an executive summary of Globex"
    
    Output:
    {{
    "tool_name": "customer_profile_tool",
    "customer_name": "Globex",
    "response_mode": "escalation"
    }}
    
    User:
    "What risks exist for Acme Corp?"
    
    Output:
    {{
    "tool_name": "customer_profile_tool",
    "customer_name": "Acme Corp",
    "response_mode": "escalation"
    }}
    ------------------------------------------------------
    IMPORTANT SAFETY RULE
    
    If response_mode = "escalation":
    
    NEVER select:
        - create_next_action_tool
        - add_issue_update_tool
    Escalation mode is for ANALYSIS.
    
    Tools that modify data are only used when the user explicitly asks to create or update records.
    
    {feedback}
    
    Return ONLY a JSON object.
    
    Every response MUST contain:
        - tool_name
        - response_mode
    
    Do not omit required fields.
    
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
    "issue_id": 3,
    "update_text": "Vendor confirmed root cause",
    "response_mode": "standard"
    }}
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
