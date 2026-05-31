from app.agent.llm import generate_response
from app.auth.tool_authorizer import authorize_tool
from app.auth.user_context import current_user


class EscalationSummarySkill:
    @staticmethod
    def execute(user_query: str, customer_data: str, conversation_history: str):
        user = current_user.get()
        authorize_tool("escalation_summary_skill", user)
        prompt = f"""
You are an enterprise customer operations assistant.
Conversation History:
{conversation_history}
User Question:
{user_query}
Customer Data:
{customer_data}
Produce the following sections:
1. Executive Summary
2. Risk Level (Low/Medium/High/Critical)
3. Recommended Next Action
4. Missing Information
Rules:
- Base the answer only on customer data
- Do not invent facts
- Be concise
- Use professional enterprise language
"""
        return generate_response(prompt)
