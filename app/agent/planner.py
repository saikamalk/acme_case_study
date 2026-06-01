from app.agent.exceptions import PlannerValidationError
from app.agent.llm import generate_plan
from app.agent.models import ToolPlan
from app.auth.tool_permissions import TOOL_PERMISSIONS
from app.auth.user_context import current_user
from app.observability.logger import logger

AVAILABLE_TOOLS = [
    "customer_profile_tool",
    "issue_history_tool",
    "create_next_action_tool",
    "add_issue_update_tool",
]
MAX_PLANNER_RETRIES = 3


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
            plan = generate_plan(f"{user_query}\n{feedback}")
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
