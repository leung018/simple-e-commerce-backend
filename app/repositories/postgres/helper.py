from app.repositories.base import LockLevel


def select_query_helper(query: str, lock_level: LockLevel):
    query = query.strip(";")
    if lock_level == lock_level.EXCLUSIVE:
        query += " FOR UPDATE"
    query += ";"
    return query
