import os
import pytest
from pathlib import Path
from insuretra_pipeline.db import connect
from insuretra_pipeline.config import get_settings

@pytest.fixture(scope="session")
def db_connection():
    settings = get_settings()
    if not settings.database_url:
        pytest.skip("DATABASE_URL is not set. Skipping DB integration tests.")
    
    url = settings.database_url
    
    # Load schema migrations in order
    migrations_dir = Path(__file__).parent.parent / "supabase" / "migrations"
    
    with connect(url) as conn:
        for sql_file in sorted(migrations_dir.glob("*.sql")):
            with open(sql_file, "r") as f:
                conn.execute(f.read())
        conn.commit()
        yield conn
