from langchain.tools import Tool

from app.agent.entity_resolver import resolve_customer_name
from app.db.queries import get_issue_updates, get_open_issues
from app.tools.customer_tools import get_customer_profile


def customer_lookup(query: str):
    customer_name = resolve_customer_name(query)
    if customer_name == "NONE":
        return {"error": "Customer not found"}
    result = get_customer_profile(customer_name)
    return str(result)


customer_profile_tool = Tool(
    name="customer_profile_tool",
    func=customer_lookup,
    description="Retrieve customer profile, open issues and customer status using customer name."
)


issue_history_tool = Tool(
    name="issue_history_tool",
    func=lambda issue_id: str(get_issue_updates(int(issue_id))),
    description="Retrieve issue update history using issue ID."
)

