from sqlalchemy import text
from mcp_server.db.connection import SessionLocal


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


def create_next_action(issue_id: int, action_text: str, created_by: str):
    session = SessionLocal()
    try:
        query = text("""
                     INSERT INTO next_actions
                     (issue_id,
                      action_text,
                      created_by)
                     VALUES (:issue_id,
                             :action_text,
                             :created_by)
                     RETURNING id
                     """)
        result = session.execute(
            query,
            {
                "issue_id": issue_id,
                "action_text": action_text,
                "created_by": created_by
            }
        )
        session.commit()
        return result.scalar()
    finally:
        session.close()


def get_next_actions(issue_id: int):
    session = SessionLocal()
    try:
        query = text("""
                     SELECT *
                     FROM next_actions
                     WHERE issue_id = :issue_id
                     ORDER BY created_at DESC
                     """)
        results = session.execute(
            query,
            {"issue_id": issue_id}
        ).mappings().all()
        return [dict(r) for r in results]
    finally:
        session.close()

def add_issue_update(issue_id: int, update_text: str):
    session = SessionLocal()
    try:
        query = text("""
                     INSERT INTO issue_updates(issue_id, update_text)
                     VALUES (:issue_id, :update_text)
                     RETURNING id
                     """)
        result = session.execute(
            query,
            {"issue_id": issue_id, "update_text": update_text}
        )
        session.commit()
        return result.scalar()
    finally:
        session.close()

def get_user_role(username: str):
    session = SessionLocal()
    try:
        query = text("""
                     SELECT role_name
                     FROM users u 
                         JOIN user_roles ur 
                         ON LOWER(u.username) = LOWER(ur.username)
                     WHERE LOWER(u.username) = LOWER(:username)
                     LIMIT 1
                     """)
        result = session.execute(
            query,
            {"username": username}
        ).mappings().first()
        return result["role_name"] if result else None
    finally:
        session.close()
