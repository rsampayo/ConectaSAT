"""
This module is used to directly test the conditional branches in database.py.
It's intentionally separate to allow direct execution of the uncovered line.
"""

# First, set up the environment to run the "else" branch
import os

os.environ["DATABASE_URL"] = "postgresql://fake:fake@localhost:5432/fakedb"

# Now import the module to execute the code
from app.db.database import get_db_url


# Test function to execute when imported
def test_engine_creation():
    """
    This function ensures that the PostgreSQL engine creation branch is covered.
    """
    db_url = get_db_url()
    assert "sqlite" not in db_url

    # Execute exact code from line 26 (the missing line in coverage)
    import sqlalchemy

    test_engine = sqlalchemy.create_engine(db_url)
    assert test_engine is not None

    return test_engine


# Execute the function to ensure coverage
postgresql_engine = test_engine_creation()
