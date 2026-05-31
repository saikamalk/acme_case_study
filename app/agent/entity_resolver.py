import json

from app.agent.llm import generate_response
from app.agent.models import CustomerResolutionResponse
from app.db.queries import get_all_customers
from app.observability.logger import logger


def resolve_customer_name(user_query: str):
    logger.info(f"Resolve Customer Name: {user_query}")
    customers = get_all_customers()
    logger.info(f"Customers Available: {customers}")
    prompt = f"""
   User Query:
   {user_query}
   Available Customers:
   {customers}
   Return response ONLY as valid JSON.
   
   Example:
   {{
        "customer_name": "ABC Corp"
   }}
   
   Rules:
   - customer_name must exactly match one customer
   - no explanations
   - no markdown
   - no extra text
   If no match exists:
   {{
        "customer_name": "NONE"
   }}
   """
    try:
        response = generate_response(prompt)
        parsed = json.loads(response)
        validated = CustomerResolutionResponse(**parsed)
        logger.info(f"Resolved Customer Name: {validated.customer_name}")
        return validated.customer_name
    except Exception as e:
        logger.error(e, exc_info=True)
        return "NONE"