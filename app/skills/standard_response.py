from app.agent.llm import generate_response


class StandardResponseSkill:
    @staticmethod
    def execute(user_query: str, customer_data: str, conversation_history: str):
        prompt = f"""
Conversation History:
{conversation_history}
User Question:
{user_query}
Retrieved Data:
{customer_data}
Answer the user's question.
Rules:
- Use only retrieved data
- Be concise
- Be professional
- Do not invent facts
"""
        return generate_response(prompt)
