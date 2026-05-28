from fastapi import FastAPI
from app.tools.customer_tools import get_customer_profile

app = FastAPI()


@app.get("/tools")
def list_tools():
    return {
        "tools": [
            "get_customer_profile"
        ]
    }


@app.get("/tool/customer_profile")
def customer_profile(customer_name: str):
    return get_customer_profile(customer_name)
