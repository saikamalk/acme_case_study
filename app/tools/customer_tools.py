from app.observability.logger import logger
from app.services.customer_service import CustomerService


def get_customer_profile(customer_name: str):
    logger.info(f"Calling Tool: get_customer_profile with customer_name: {customer_name}")
    result = CustomerService.fetch_customer_profile(customer_name)
    logger.info(f"Tool Completed: get_customer_profile. Result:\n{result}")
    return result
