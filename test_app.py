import os
import pytest
import tempfile

import app

def test_db_table():
    assert "users" in app.db.metadata.tables.keys()

def test_db_fields():
    field_set= set(["id","username","email","password_hash","date_created"])
    db_field_set = set(app.db.metadata.tables["users"].columns.keys())
    assert len(db_field_set.intersection(field_set)) == len(field_set)

def test_create_user():
    user = app.User(username='peter', email='peter@example.org')
    user.set_hash_password("Passw0rd!")
    app.db.session.add(user)
    app.db.session.commit()
    assert len(app.User.query.filter_by(username='peter').filter_by(email='peter@example.org').all()) == 1

def test_user_authentificate():
    user=app.User.query.filter_by(username='peter').filter_by(email='peter@example.org').first()
    assert user.authentificate("Passw0rd!")

def test_user_check_password():
    user=app.User.query.filter_by(username='peter').filter_by(email='peter@example.org').first()
    assert user.check_password("Passw0rd!")

def test_delete_user():
    user=app.User.query.filter_by(username='peter').filter_by(email='peter@example.org').first()
    app.db.session.delete(user)
    app.db.session.commit()
    assert len(app.User.query.filter_by(username='peter').filter_by(email='peter@example.org').all()) == 0