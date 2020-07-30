import os
import pytest
import tempfile

import app

@pytest.fixture
def client():
    db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True

    with app.app.test_client() as client:
        with app.app.app_context():
            app.init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.app.config['DATABASE'])

def test_db_table(client):
    assert "users" in app.db.metadata.tables.keys()

def test_db_fields(client):
    field_set= set(["id","username","email","password_hash","date_created"])
    db_field_set = set(app.db.metadata.tables["users"].columns.keys())
    assert len(db_field_set.intersection(field_set)) == len(field_set)

def test_create_user(client):
    user = app.User(username='peter', email='peter@example.org')
    user.set_hash_password("Passw0rd!")
    app.db.session.add(user)
    app.db.session.commit()
    assert len(app.User.query.filter_by(username='peter').filter_by(email='peter@example.org').all()) == 1

def test_user_authentificate(client):
    user=app.User.query.filter_by(username='peter').filter_by(email='peter@example.org').first()
    assert user.authentificate("Passw0rd!")

def test_user_check_password(client):
    user=app.User.query.filter_by(username='peter').filter_by(email='peter@example.org').first()
    assert user.check_password("Passw0rd!")

def test_delete_user(client):
    user=app.User.query.filter_by(username='peter').filter_by(email='peter@example.org').first()
    app.db.session.delete(user)
    app.db.session.commit()
    assert len(app.User.query.filter_by(username='peter').filter_by(email='peter@example.org').all()) == 0