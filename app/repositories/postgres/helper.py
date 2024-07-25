def select_query_helper(query: str, for_share: bool):
    query = query.strip(";")
    if for_share:
        query += " FOR SHARE"
    query += ";"
    return query
