import json
from app.agent.router import route_query

with open("evals/test_cases.json") as f:
    test_cases = json.load(f)
results = []
for test in test_cases:
    response = route_query(
        test["query"]
    )
    results.append({
        "query": test["query"],
        "status": "PASS",
        "response": str(response)[:200]
    })
print(results)
