import json
import os

import httpx
from dotenv import load_dotenv
from groq import Groq

from app.agent.models import ToolPlan

load_dotenv()
insecure_http_client = httpx.Client(verify=False)

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
    http_client=insecure_http_client
)


def generate_response(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )
    return response.choices[0].message.content

def generate_plan(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": f"{prompt}\n\nReturn ONLY JSON"
            }
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    content = response.choices[0].message.content
    parsed = json.loads(content)
    return ToolPlan(**parsed)
