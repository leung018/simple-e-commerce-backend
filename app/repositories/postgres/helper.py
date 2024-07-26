def select_query_helper(query: str, for_update: bool):
    query = query.strip(";")
    if for_update:
        query += " FOR UPDATE"
    query += ";"
    return query
