import asyncio

from app.agent.exceptions import PlannerValidationError
from app.agent.executor import execute_plan
from app.agent.planner import create_plan
from app.cache.memory import get_conversation_history, save_message
from app.observability.logger import logger
from app.observability.trace_store import tracer
from app.skills.escalation_summary import EscalationSummarySkill
from app.skills.standard_response import StandardResponseSkill


async def route_query_async(user_query: str, user: dict):
    try:
        logger.info(f"User Query:\n{user_query}")
        history = await asyncio.to_thread(get_conversation_history, user["username"])
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
        with tracer.start_as_current_span("planner") as span:
            plan = await asyncio.to_thread(create_plan, enriched_query)
            span.set_attribute("tool.selected", plan.tool_name)
            span.set_attribute("response.mode", plan.response_mode)
        logger.info(f"Plan Created:\n{plan.model_dump()}")

        if plan.customer_name:
            tool_input = str(plan.customer_name)
        elif plan.issue_id:
            tool_input = str(plan.issue_id)
        elif plan.action_text:
            tool_input = str(plan.action_text)
        else:
            tool_input = ""

        with tracer.start_as_current_span("tool_execution") as span:
            tool_output = await execute_plan(plan)
            span.set_attribute("tool.name", plan.tool_name)
            span.set_attribute("tool.input", str(tool_input))
            span.set_attribute("tool.output", str(tool_output))
        logger.info(f"Tool Output:\n{tool_output}")
        logger.info(f"Skill selected: {plan.response_mode}")
        with tracer.start_as_current_span("skill_execution") as span:
            if plan.response_mode == "escalation":
                final_response = await asyncio.to_thread(
                    EscalationSummarySkill.execute,
                    user_query, tool_output, history_text
                )
            else:
                final_response = await asyncio.to_thread(
                    StandardResponseSkill.execute,
                    user_query, tool_output, history_text
                )
            span.set_attribute("response.mode", plan.response_mode)
            span.set_attribute("response.output", str(final_response))
        await asyncio.to_thread(save_message, user["username"], "user", user_query)
        await asyncio.to_thread(save_message, user["username"], f"{plan.tool_name} output", tool_output)
        await asyncio.to_thread(save_message, user["username"], "assistant", final_response)
        logger.info(f"Final Response:\n{final_response}")
        return final_response
    except PlannerValidationError as e:
        logger.error(f"PLANNER_ERROR={str(e)}", exc_info=True)
        return "I could not confidently determine the customer or issue referenced in your request. Please provide additional details."
    except Exception as e:
        logger.error(f"AGENT_ERROR={str(e)}", exc_info=True)
        return {"error": str(e)}


def route_query(user_query: str, user: dict):
    return asyncio.run(route_query_async(user_query, user))
