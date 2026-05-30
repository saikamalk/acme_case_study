from app.observability.logger import logger
from app.services.customer_service import CustomerService


def get_customer_profile(customer_name: str):
    logger.info(f"TOOL_CALLED=get_customer_profile CUSTOMER={customer_name}")
    result = CustomerService.fetch_customer_profile(customer_name)
    logger.info(f"TOOL_COMPLETED=get_customer_profile; result={result}")
    logger.info("EVAL_TOOL=customer_profile_tool")
    return result
