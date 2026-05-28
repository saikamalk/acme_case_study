from pydantic import BaseModel


class CustomerResolutionResponse(BaseModel):
    customer_name: str