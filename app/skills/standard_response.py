from app.agent.llm import generate_response


class StandardResponseSkill:
    @staticmethod
    def execute(user_query: str, customer_data: str, conversation_history: str):
        facts = generate_response(f"""
        Extract only the facts relevent to answering this question. 
        Question: {user_query}
        Raw data: {customer_data}
        Return bullet points. No explanations. No invented facts.
        """)
        gaps = generate_response(f"""
        Given these facts:
        {facts}
        Is there anything missing that would be needed to fully answer this question?
        Question: {user_query}
        Reply with either "None" or a short bullet list of missing items.
        """)
        prompt = f"""
                Conversation History:
                {conversation_history}
                User Question:{user_query}
                Relevant facts: {facts}
                Missing information: {gaps}
                
                Answer the user's question using only the facts above.
                Rules:
                - Be concise and professional
                - Do not invent facts
                - If information is missing, say so briefly
                - No section headers, just a clean direct answer
                """
        return generate_response(prompt)
