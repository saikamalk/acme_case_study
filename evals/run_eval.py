import json
import time
import traceback
from pathlib import Path
from app.agent.router import route_query
from app.auth.user_context import current_user
from app.observability.trace_store import TRACE_STORE, get_traces

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
    "couldn't find"
    "no customer",
    "no issue",
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


def extract_latest_traces(before_len: int):
    """
    TRACE_STORE is appendleft-based, so the newest traces are at the front.
    """
    after = list(get_traces())
    new_count = max(0, len(after) - before_len)
    return after[:new_count]


def get_trace_value(traces, trace_type: str, key: str):
    for trace in traces:
        if trace.get("type") == trace_type and key in trace:
            return trace.get(key)
    return None


with open(TEST_CASES_PATH) as f:
    test_cases = json.load(f)
# Start each evaluation run from a clean trace store.
TRACE_STORE.clear()
results = []
for test in test_cases:
    user = {
        "username": test["username"],
        "roles": test["roles"],
    }
    current_user.set(user)
    before_len = len(get_traces())
    outcome = None
    error_text = ""
    trace_text = ""
    status = "FAIL"
    passed_checks = []
    failed_checks = []
    try:
        outcome = route_query(test["query"], user)
        outcome_text = normalize_text(outcome)
    except Exception as e:
        outcome = None
        outcome_text = ""
        error_text = f"{type(e).__name__}: {e}"
        trace_text = traceback.format_exc()
    new_traces = extract_latest_traces(before_len)
    selected_tool = get_trace_value(new_traces, "agent", "selected_tool")
    selected_skill = get_trace_value(new_traces, "skill", "selected_skill")
    actual_tool_input = get_trace_value(new_traces, "agent", "tool_input")
    tool_output = get_trace_value(new_traces, "tool_execution", "tool_output")
    # Use the response body / returned object, not HTTP semantics.
    response_text = normalize_text(outcome)
    if not response_text and error_text:
        response_text = error_text
    # --- expected_tool ---
    if "expected_tool" in test:
        if selected_tool == test["expected_tool"]:
            passed_checks.append(f"tool={selected_tool}")
        else:
            failed_checks.append(
                f"expected_tool={test['expected_tool']}, actual_tool={selected_tool}"
            )
    # --- expected_response_mode ---
    if "expected_response_mode" in test:
        if selected_skill == test["expected_response_mode"]:
            passed_checks.append(f"response_mode={selected_skill}")
        else:
            failed_checks.append(
                f"expected_response_mode={test['expected_response_mode']}, actual_response_mode={selected_skill}"
            )
    # --- expected_error ---
    # Since route_query() does not return an HTTP status code, this test runner
    # treats a denial as passing only if the response/error text clearly indicates
    # the request was rejected.
    if "expected_error" in test:
        expected_error = str(test["expected_error"])
        denial_like = contains_any(response_text, DENIAL_PATTERNS)
        # If the output is a normal assistant answer, this must fail.
        # If the output is an error-like response, require denial wording.
        if denial_like or expected_error in response_text:
            passed_checks.append(f"expected_error={expected_error}")
        else:
            failed_checks.append(
                f"expected_error={expected_error}, actual_response={response_text[:200]}"
            )
    # --- expected_customer_not_found ---
    if test.get("expected_customer_not_found"):
        if contains_any(response_text, NOT_FOUND_PATTERNS):
            passed_checks.append("customer_not_found")
        else:
            failed_checks.append(
                f"expected_customer_not_found=true, actual_response={response_text[:200]}"
            )
    # --- expected_not_found ---
    if test.get("expected_not_found"):
        if contains_any(response_text, NOT_FOUND_PATTERNS):
            passed_checks.append("not_found")
        else:
            failed_checks.append(
                f"expected_not_found=true, actual_response={response_text[:200]}"
            )
    # --- expected_grounded ---
    # Keep this conservative: a grounded answer must not look like a fallback
    # and should have used a real tool trace.
    if test.get("expected_grounded"):
        if selected_tool and tool_output and not contains_any(
                response_text, PLANNER_FALLBACK_PATTERNS
        ):
            passed_checks.append("grounded")
        else:
            failed_checks.append(
                f"expected_grounded=true, selected_tool={selected_tool}, tool_output_present={bool(tool_output)}"
            )
    # --- expected_result_contains (legacy support) ---
    if "expected_result_contains" in test:
        expected_snippet = str(test["expected_result_contains"])
        if expected_snippet in response_text:
            passed_checks.append(f"contains={expected_snippet}")
        else:
            failed_checks.append(
                f"expected_result_contains={expected_snippet}, actual_response={response_text[:200]}"
            )
    # Final status
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
