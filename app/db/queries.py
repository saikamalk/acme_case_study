from sqlalchemy import text
from app.db.connection import SessionLocal


def get_all_customers():
    session = SessionLocal()
    try:
        query = text("""
                     SELECT name
                     FROM customers
                     """)
        results = session.execute(
            query
        ).mappings().all()
        return [row["name"] for row in results]
    finally:
        session.close()


def get_customer_by_name(name: str):
    session = SessionLocal()
    try:
        query = text("""
                     SELECT *
                     FROM customers
                     WHERE LOWER(name) = LOWER(:name)
                     """)
        result = session.execute(
            query,
            {"name": name}
        ).mappings().first()
        return dict(result) if result else None
    finally:
        session.close()


def get_open_issues(customer_id: int):
    session = SessionLocal()
    try:
        query = text("""
                     SELECT *
                     FROM issues
                     WHERE customer_id = :customer_id
                       AND status IN ('Open', 'Escalated')
                     """)
        results = session.execute(
            query,
            {"customer_id": customer_id}
        ).mappings().all()
        return [dict(row) for row in results]
    finally:
        session.close()


def get_issue_updates(issue_id: int):
    session = SessionLocal()
    try:
        query = text("""
                     SELECT *
                     FROM issue_updates
                     WHERE issue_id = :issue_id
                     ORDER BY created_at DESC
                     """)
        results = session.execute(
            query,
            {"issue_id": issue_id}
        ).mappings().all()
        return [dict(row) for row in results]
    finally:
        session.close()
