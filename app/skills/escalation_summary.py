from app.agent.llm import generate_response


class EscalationSummarySkill:
    @staticmethod
    def execute(customer_data):
        prompt = f"""
       You are an enterprise support assistant.
       Analyze this customer situation.
       Customer Data:
       {customer_data}
       Return:
       1. Executive summary
       2. Risk level
       3. Recommended next action
       4. Missing information
       Keep response concise and professional.
       """
        response = generate_response(prompt)
        return response
