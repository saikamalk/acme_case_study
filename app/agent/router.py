from app.agent.agent import agent_executor
from app.agent.llm import generate_response
from app.cache.memory import get_conversation_history, save_message
from app.observability.logger import logger


def route_query(user_query: str, username: str):
    try:
        logger.info(f"USER_QUERY={user_query}, USERNAME={username}")
        history = get_conversation_history(username)
        history_text = ""
        for item in history:
            history_text += f"{item['role']}: {item['message']}\n"

        enriched_query = f"""
        Conversation History:
        {history_text}
        
        Current User Query:
        {user_query}
        """
        logger.info(f"ENRICHED_QUERY={enriched_query}")
        agent_response = agent_executor.invoke(
            {
                "input": enriched_query,
                "username": username,
            }
        )
        tool_output = agent_response.get("output", "")
        synthesis_prompt = f"""
        Conversation History:
        {history_text}
        
        User Question:
        {user_query}
        
        Retrieved Enterprise Data:
        {tool_output}
        
        TASK:
        Generate a concise enterprise support response.
        
        Include:
        - customer situation summary
        - issue severity
        - operational risks
        - recommended next action
        
        Keep response professional
        """

        final_response = generate_response(synthesis_prompt)
        save_message(username, "user", user_query)
        save_message(username, "assistant", final_response)
        return final_response
    except Exception as e:
        logger.error(f"AGENT_ERROR={str(e)}", exc_info=True)
        return {"error": str(e)}
