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
    
    # Load schema (ensure it is safe to run on the target DB)
    schema_path = Path(__file__).parent.parent / "supabase" / "migrations" / "001_insuretra_pipeline.sql"
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    with connect(url) as conn:
        conn.execute(schema_sql)
        conn.commit()
        yield conn
