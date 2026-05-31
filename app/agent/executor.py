from app.agent.tools import customer_lookup, issue_history_lookup
from app.tools.issue_update_tools import add_issue_update_tool
from app.tools.next_action_tools import create_next_action_tool


def execute_plan(plan):
    if plan.tool_name == "customer_profile_tool":
        return customer_lookup(plan.customer_name)
    if plan.tool_name == "issue_history_tool":
        return issue_history_lookup(str(plan.issue_id))
    if plan.tool_name == "create_next_action_tool":
        return create_next_action_tool(plan.issue_id, plan.action_text)
    if plan.tool_name == "add_issue_update_tool":
        return add_issue_update_tool(plan.issue_id, plan.update_text)
    raise ValueError(f"Unknown tool: {plan.tool_name}")
