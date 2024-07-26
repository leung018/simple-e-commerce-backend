from app.repositories.base import LockLevel


def select_query_helper(query: str, lock_level: LockLevel):
    query = query.strip(";")

    match lock_level:
        case LockLevel.EXCLUSIVE:
            query += " FOR UPDATE"
        case LockLevel.NONE:
            """Do nothing"""

    query += ";"
    return query
