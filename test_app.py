import pytest

import app

def test_db_table():
    assert "users" in app.db.metadata.tables.keys()