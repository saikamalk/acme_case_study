from app.agent.exceptions import PlannerValidationError
from app.agent.executor import execute_plan
from app.agent.planner import create_plan
from app.cache.memory import get_conversation_history, save_message
from app.observability.logger import logger
from app.observability.trace_store import add_trace
from app.skills.escalation_summary import EscalationSummarySkill
from app.skills.standard_response import StandardResponseSkill


def route_query(user_query: str, user: dict):
    try:
        logger.info(f"User Query:\n{user_query}")
        history = get_conversation_history(user["username"])
        history_text = ""
        for item in history:
            history_text += f"{item['role']}: {item['message']}\n"

        enriched_query = f"""
        Conversation History:
        {history_text}
        
        Current User Query:
        {user_query}
        """
        logger.info(f"Enriched Query:\n{enriched_query}")
        plan = create_plan(enriched_query)
        logger.info(f"Plan Created:\n{plan.model_dump()}")

        if plan.customer_name:
            tool_input = str(plan.customer_name)
        elif plan.issue_id:
            tool_input = str(plan.issue_id)
        elif plan.action_text:
            tool_input = str(plan.action_text)
        elif plan.tool_input:
            tool_input = str(plan.tool_input)
        else:
            tool_input = ""

        add_trace(
            {
                "type": "agent",
                "username": user["username"],
                "query": user_query,
                "selected_tool": plan.tool_name,
                "tool_input": tool_input,
            }
        )
        tool_output = execute_plan(plan)
        logger.info(f"Tool Output:\n{tool_output}")
        add_trace(
            {
                "type": "tool_execution",
                "username": user["username"],
                "tool_name": plan.tool_name,
                "tool_output": str(tool_output)[:500]
            }
        )
        add_trace(
            {
                "type": "skill",
                "username": user["username"],
                "selected_skill": plan.response_mode,
            }
        )
        logger.info(f"Skill selected:\n{plan.response_mode}")
        if plan.response_mode == "escalation":
            final_response = EscalationSummarySkill.execute(user_query, tool_output, history_text)
        else:
            final_response = StandardResponseSkill.execute(user_query, tool_output, history_text)
        save_message(user["username"], "user", user_query)
        save_message(user["username"], "assistant", final_response)
        logger.info(f"Final Response:\n{final_response}")
        return final_response
    except PlannerValidationError as e:
        logger.error(f"PLANNER_ERROR={str(e)}", exc_info=True)
        return "I could not confidently determine the customer or issue referenced in your request. Please provide additional details."
    except Exception as e:
        logger.error(f"AGENT_ERROR={str(e)}", exc_info=True)
        return {"error": str(e)}
