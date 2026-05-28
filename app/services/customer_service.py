from app.db.queries import (
    get_customer_by_name,
    get_open_issues,
    get_issue_updates
)


class CustomerService:
    @staticmethod
    def fetch_customer_profile(customer_name: str):
        customer = get_customer_by_name(customer_name)
        if not customer:
            return None
        issues = get_open_issues(customer["id"])
        for issue in issues:
            updates = get_issue_updates(issue["id"])
            issue["updates"] = updates
        customer["open_issues"] = issues
        return customer
