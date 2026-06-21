from sqlalchemy import inspect, text

from app.database import engine


def run_migrations() -> None:
    """Add new columns to existing SQLite databases without dropping data."""
    column_migrations = [
        ("sources", "folder_path", "VARCHAR(500)"),
        ("domains", "folder_path", "VARCHAR(500)"),
        ("projects", "folder_path", "VARCHAR(500)"),
        ("web_pages", "source_file_path", "VARCHAR(1000)"),
        ("chunks", "embedding_provider", "VARCHAR(20)"),
    ]
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table, column, col_type in column_migrations:
            if table not in inspector.get_table_names():
                continue
            existing = {c["name"] for c in inspector.get_columns(table)}
            if column not in existing:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
