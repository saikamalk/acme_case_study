from app.agent.llm import generate_response


class EscalationSummarySkill:
    @staticmethod
    def execute(user_query: str, customer_data: str, conversation_history: str):
        facts = generate_response(f"Extract key facts from this data as bullet points:\n{customer_data}")
        risk = generate_response(
            f"Given these facts:\n{facts}\n Assign a risk level: Low/Medium/High/Critical. Reply with one word.")
        recommendation = generate_response(
            f"Given risk={risk} and facts:\n{facts}\nSuggest a single concrete next action.")
        gaps = generate_response(
            f"Given facts:\n{facts}\nWhat key information is missing to fully assess this customer?")
        return generate_response(
            f"""
            User question: {user_query}
            Facts: {facts}
            Risk: {risk}
            Recommendation: {recommendation}
            Missing info: {gaps}
            Write an executive summary with four sections above. Be concise and professional.
            """
        )
