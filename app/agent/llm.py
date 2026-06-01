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


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "customer_profile_tool",
            "description": """
            Retrieve customer profile information.
            
            Use this as the default tool when the user asks about a customer/company, including:
            - customer details
            - customer profile
            - customer information
            - account information
            - customer status
            - open issues for a customer
            - all issues for a customer
            - situation of a customer
            - executive summary for a customer
            
            Examples:
            - "Show open issues for Globex" -> customer_profile_tool
            - "How bad is Globex's situation?" -> customer_profile_tool
            
            Do NOT use for:
            - issue history by issue id
            - issue timeline
            - issue updates
            - next actions
            - next steps
            - action plans
            - recommendations
            - creating records
            - saving records
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_name": {
                        "type": "string",
                        "description": "The customer/company name to look up.",
                    },
                    "response_mode": {
                        "type": "string",
                        "enum": ["standard", "escalation"],
                        "description": "standard for factual lookups, escalation for risk/executive analysis"
                    }
                },
                "required": ["customer_name", "response_mode"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "issue_history_tool",
            "description": """
            Retrieve issue history and issue details.
            
            Use ONLY when the user explicitly provides an issue id/number.
            Examples:
            - "Show issue 12 history" -> issue_history_tool
            - "What is the status of issue 7?" -> issue_history_tool
            
            Do NOT use if the request only mentions a customer/company name.
            Do NOT infer or fabricate issue_id from customer name.
            Do NOT use for:
            - customer profile lookup
            - open issues for a customer
            - executive summary for a customer
            - next actions
            - adding updates
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_id": {
                        "type": "integer",
                        "description": "The explicit issue ID to retrieve history for"
                    },
                    "response_mode": {
                        "type": "string",
                        "enum": ["standard", "escalation"],
                        "description": "Almost always standard for issue history"
                    }
                },
                "required": ["issue_id", "response_mode"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_next_action_tool",
            "description": """
            Create and save a next action for an issue.
            Use when the user asks:
            - create next action
            - add next action
            - save next action
            - insert next action
            - create next actions
            - add action item
            - create action item
            If the request contains both:
            - an issue reference
            and
            - an action description
            then prefer this tool over all other tools.
            Examples:
            - Create next action for issue 3. Action is fix to be deployed.
            - Add next action for issue 5: Contact customer.
            - Save next action for issue 2.
            Do NOT use for:
            - viewing issue history
            - viewing customer profiles
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_id": {
                        "type": "integer",
                        "description": "The issue ID to create a next action for"
                    },
                    "action_text": {
                        "type": "string",
                        "description": "The recommended action to record"
                    },
                    "response_mode": {
                        "type": "string",
                        "enum": ["standard", "escalation"],
                        "description": "Almost always standard"
                    }
                },
                "required": ["issue_id", "action_text", "response_mode"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_issue_update_tool",
            "description": """
            Add and save an update to an issue.
            Use when the user asks:
            - add update
            - create update
            - save update
            - post update
            - update issue
            Do NOT use for:
            - creating next actions
            - customer profile lookup
            - issue history retrieval
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_id": {
                        "type": "integer",
                        "description": "The issue ID to update"
                    },
                    "update_text": {
                        "type": "string",
                        "description": "The update text to record"
                    },
                    "response_mode": {
                        "type": "string",
                        "enum": ["standard", "escalation"],
                        "description": "Almost always standard"
                    }
                },
                "required": ["issue_id", "update_text", "response_mode"]
            }
        }
    }
]


def generate_plan(user_query: str) -> ToolPlan:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
                You are an enterprise tool planner.
                
                You MUST choose exactly one tool from the provided tool list.
                
                Allowed tools:
                - customer_profile_tool
                - issue_history_tool
                - create_next_action_tool
                - add_issue_update_tool
                
                Never call, reference, or invent any other tool.
                
                Do not use:
                - brave_search
                - web_search
                - search
                - internet_search
                - google_search
                - browser
                If none of the allowed tools can satisfy the request,
                choose the closest allowed tool and populate its arguments appropriately.
                
                You must only return a tool call from the allowed tool list.
                """
            },
            {
                "role": "user",
                "content": user_query
            }
        ],
        tools=TOOL_SCHEMAS,
        tool_choice="required",
        temperature=0
    )
    tool_call = response.choices[0].message.tool_calls[0]
    args = json.loads(tool_call.function.arguments)
    return ToolPlan(tool_name=tool_call.function.name, **args)
