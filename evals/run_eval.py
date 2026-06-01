import asyncio
import json
import time
import traceback
from pathlib import Path
from app.agent.router import route_query_async
from app.auth.user_context import current_user

EVAL_DIR = Path("evals")
TEST_CASES_PATH = EVAL_DIR / "test_cases.json"
RESULTS_PATH = EVAL_DIR / "results.json"
DENIAL_PATTERNS = [
    "403",
    "forbidden",
    "not authorized",
    "permission denied",
    "access denied",
    "unauthorized",
]
NOT_FOUND_PATTERNS = [
    "not found",
    "could not find",
    "couldn't find",
    "no customer",
    "no issue",
    "no data",
    "no history",
    "no information",
    "unknown customer",
    "unknown issue",
]
PLANNER_FALLBACK_PATTERNS = [
    "could not confidently determine",
    "please provide additional details",
]


def normalize_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def contains_any(text: str, patterns) -> bool:
    lower_text = text.lower()
    return any(pattern.lower() in lower_text for pattern in patterns)


class PlanCapture:
    """
    Lightweight capture of planner decisions per eval run.
    Replaces the old TRACE_STORE dependency.
    """

    def __init__(self):
        self.selected_tool = None
        self.selected_skill = None
        self.tool_input = None
        self.tool_output = None

    def reset(self):
        self.selected_tool = None
        self.selected_skill = None
        self.tool_input = None
        self.tool_output = None


capture = PlanCapture()


def _patch_router():
    """
    Monkey-patch route_query_async to capture planner decisions
    without needing TRACE_STORE.
    """
    import app.agent.router as router_module

    async def patched_route(user_query: str, user: dict):
        capture.reset()
        from app.agent.planner import create_plan
        from app.agent.executor import execute_plan
        import asyncio
        history = await asyncio.to_thread(
            __import__("app.cache.memory", fromlist=["get_conversation_history"])
            .get_conversation_history, user["username"]
        )
        history_text = "".join(
            f"{item['role']}: {item['message']}\n" for item in history
        )
        enriched_query = f"Conversation History:\n{history_text}\nCurrent User Query:\n{user_query}"
        plan = await asyncio.to_thread(create_plan, enriched_query)
        capture.selected_tool = plan.tool_name
        capture.selected_skill = plan.response_mode
        if plan.customer_name:
            capture.tool_input = str(plan.customer_name)
        elif plan.issue_id:
            capture.tool_input = str(plan.issue_id)
        elif plan.action_text:
            capture.tool_input = str(plan.action_text)
        else:
            capture.tool_input = ""
        tool_output = await execute_plan(plan)
        capture.tool_output = str(tool_output)[:500]
        from app.skills.escalation_summary import EscalationSummarySkill
        from app.skills.standard_response import StandardResponseSkill
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
        from app.cache.memory import save_message
        await asyncio.to_thread(save_message, user["username"], "user", user_query)
        await asyncio.to_thread(save_message, user["username"], f"{plan.tool_name} output", str(tool_output))
        await asyncio.to_thread(save_message, user["username"], "assistant", final_response)
        return final_response

    router_module.route_query_async = patched_route


_patch_router()
with open(TEST_CASES_PATH) as f:
    test_cases = json.load(f)
results = []
for test in test_cases:
    user = {
        "username": test["username"],
        "roles": test["roles"],
    }
    current_user.set(user)
    outcome = None
    error_text = ""
    trace_text = ""
    status = "FAIL"
    passed_checks = []
    failed_checks = []
    try:
        outcome = asyncio.run(route_query_async(test["query"], user))
        outcome_text = normalize_text(outcome)
    except Exception as e:
        outcome = None
        outcome_text = ""
        error_text = f"{type(e).__name__}: {e}"
        trace_text = traceback.format_exc()
    selected_tool = capture.selected_tool
    selected_skill = capture.selected_skill
    actual_tool_input = capture.tool_input
    tool_output = capture.tool_output
    response_text = normalize_text(outcome)
    if not response_text and error_text:
        response_text = error_text
    if "expected_tool" in test:
        if selected_tool == test["expected_tool"]:
            passed_checks.append(f"tool={selected_tool}")
        else:
            failed_checks.append(
                f"expected_tool={test['expected_tool']}, actual_tool={selected_tool}"
            )
    if "expected_response_mode" in test:
        if selected_skill == test["expected_response_mode"]:
            passed_checks.append(f"response_mode={selected_skill}")
        else:
            failed_checks.append(
                f"expected_response_mode={test['expected_response_mode']}, actual_response_mode={selected_skill}"
            )
    if "expected_error" in test:
        expected_error = str(test["expected_error"])
        denial_like = contains_any(response_text, DENIAL_PATTERNS)
        if denial_like or expected_error in response_text:
            passed_checks.append(f"expected_error={expected_error}")
        else:
            failed_checks.append(
                f"expected_error={expected_error}, actual_response={response_text[:200]}"
            )
    if test.get("expected_customer_not_found"):
        if contains_any(response_text, NOT_FOUND_PATTERNS):
            passed_checks.append("customer_not_found")
        else:
            failed_checks.append(
                f"expected_customer_not_found=true, actual_response={response_text[:200]}"
            )
    if test.get("expected_not_found"):
        if contains_any(response_text, NOT_FOUND_PATTERNS):
            passed_checks.append("not_found")
        else:
            failed_checks.append(
                f"expected_not_found=true, actual_response={response_text[:200]}"
            )
    if test.get("expected_grounded"):
        if selected_tool and tool_output and not contains_any(
                response_text, PLANNER_FALLBACK_PATTERNS
        ):
            passed_checks.append("grounded")
        else:
            failed_checks.append(
                f"expected_grounded=true, selected_tool={selected_tool}, tool_output_present={bool(tool_output)}"
            )
    if "expected_result_contains" in test:
        expected_snippet = str(test["expected_result_contains"])
        if expected_snippet in response_text:
            passed_checks.append(f"contains={expected_snippet}")
        else:
            failed_checks.append(
                f"expected_result_contains={expected_snippet}, actual_response={response_text[:200]}"
            )
    if not failed_checks:
        status = "PASS"
    results.append(
        {
            "name": test["name"],
            "status": status,
            "username": test["username"],
            "roles": test["roles"],
            "query": test["query"],
            "selected_tool": selected_tool,
            "selected_skill": selected_skill,
            "tool_input": actual_tool_input,
            "response": response_text[:1000],
            "passed_checks": passed_checks,
            "failed_checks": failed_checks,
            "error": error_text,
            "trace": trace_text,
        }
    )
    time.sleep(1)
with open(RESULTS_PATH, "w") as f:
    json.dump(results, f, indent=2)
print(json.dumps(results, indent=2))
