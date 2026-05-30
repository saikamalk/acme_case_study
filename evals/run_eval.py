import json
import time
import traceback
from app.agent.router import route_query
from app.auth.user_context import current_user

with open("evals/test_cases.json") as f:
    test_cases = json.load(f)
results = []
for test in test_cases:
    user = {
        "username": test["username"],
        "roles": test["roles"]
    }
    current_user.set(user)
    try:
        response = route_query(test["query"], user)
        status = "PASS"
        if "expected_result_contains" in test and test["expected_result_contains"] not in str(response):
            status = "FAIL"
        results.append(
            {
                "name": test["name"],
                "status": status,
                "response": str(response)[:500]
            }
        )
    except Exception as e:
        expected_error = test.get("expected_error")
        if expected_error and expected_error in str(e):
            status = "PASS"
        else:
            status = "FAIL"
        results.append(
            {
                "name": test["name"],
                "status": status,
                "error": str(e),
                "trace": traceback.format_exc()
            }
        )
    time.sleep(10)
with open("evals/results.json", "w") as f:
    json.dump(results, f, indent=2)
print(json.dumps(results, indent=2))
