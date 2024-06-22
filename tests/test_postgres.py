from app.postgres import new_postgres_conn, new_postgres_context_from_env


def test_verify_conn():
    conn = new_postgres_conn(new_postgres_context_from_env())
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            assert result is not None
