import os
from app.dependencies import get_repository_session
from app.repositories.migration import migrate_up


if __name__ == "__main__":
    csv_file_path = os.path.join("/docker-entrypoint-initdb.d/products.csv")

    session = get_repository_session()
    migrate_up(session)
    with session:
        with session.new_operator() as cur:
            cur.execute(
                f"COPY products (id, name, price, quantity, category) FROM '{csv_file_path}' DELIMITER ',' CSV HEADER;"
            )
        session.commit()
