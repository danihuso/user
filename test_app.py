import os
import jwt
import pytest
import tempfile
from datetime import datetime, timedelta

import app

@pytest.fixture
def client():
    db_fd, app.app.config["DATABASE"] = tempfile.mkstemp()
    app.app.config["TESTING"] = True

    with app.app.test_client() as client:
        with app.app.app_context():
            app.init_db()
        yield client

    os.close(db_fd)
    os.unlink(app.app.config["DATABASE"])

def test_db_table(client):
    assert "users" in app.db.metadata.tables.keys()

def test_db_fields(client):
    field_set= set(["id","username","email","password_hash","date_created"])
    db_field_set = set(app.db.metadata.tables["users"].columns.keys())
    assert len(db_field_set.intersection(field_set)) == len(field_set)

def test_db_create_user(client):
    user = app.User(username="peter", email="peter@example.org")
    user.set_hash_password("Passw0rd!")
    app.db.session.add(user)
    app.db.session.commit()
    assert len(app.User.query.filter_by(username="peter").filter_by(email="peter@example.org").all()) == 1

def test_db_user_authentificate(client):
    user=app.User.query.filter_by(username="peter").filter_by(email="peter@example.org").first()
    assert user.authentificate("Passw0rd!")

def test_db_delete_user(client):
    user=app.User.query.filter_by(username="peter").filter_by(email="peter@example.org").first()
    app.db.session.delete(user)
    app.db.session.commit()
    assert len(app.User.query.filter_by(username="peter").filter_by(email="peter@example.org").all()) == 0

def test_POST_user(client):
    rv = client.post("/api/users", json={"username":"John","email": "john@example.com", "password": "Passw0rd!"})
    json_data = rv.get_json()
    assert "date" in json_data

def test_POST_user_exist(client):
    rv = client.post("/api/users", json={"username":"John","email": "john@example.com", "password": "Passw0rd!"})
    json_data = rv.get_json()
    assert "user already exist" == json_data["text"]

def test_POST_user_missing_parameter(client):
    rv = client.post("/api/users", json={"username":"Jack"})
    json_data = rv.get_json()
    assert "missing parameter" == json_data["text"]

def test_POST_user_invalid_password(client):
    rv = client.post("/api/users", json={"username":"Jack","email": "jack@example.com", "password": "secret"})
    json_data = rv.get_json()
    assert "Password should be at least 8 characters with 1 Uppercase, 1 number, and and 1 special character" == json_data["text"]

def test_POST_user_invalid_email(client):
    rv = client.post("/api/users", json={"username":"Jack","email": "Jackexample.com", "password": "Passw0rd!"})
    json_data = rv.get_json()
    assert "Please use a valid email" == json_data["text"]

def test_GET_user_token(client):
    rv = client.get("/api/users", json={"username":"John", "password": "Passw0rd!"})
    json_data = rv.get_json()
    assert "token" in json_data

def test_GET_user_missing_parameter(client):
    rv = client.get("/api/users", json={"username":"John"})
    json_data = rv.get_json()
    assert "missing parameter" == json_data["text"]

def test_GET_user_wrong_user(client):
    rv = client.get("/api/users", json={"username":"wrongUser", "password": "Passw0rd!"})
    json_data = rv.get_json()
    assert "login incorrect" == json_data["text"]

def test_GET_user_wrong_password(client):
    rv = client.get("/api/users", json={"username":"John", "password": "wrongPassword"})
    json_data = rv.get_json()
    assert "login incorrect" == json_data["text"]

def test_DELETE_user_missing_parameter(client):
    rv = client.delete("/api/users", json={"param":"none"})
    json_data = rv.get_json()
    assert "missing parameter" == json_data["text"]

def test_DELETE_user_invalid_token(client):
    rv = client.delete("/api/users", json={"token":"invalidtoken"})
    json_data = rv.get_json()
    assert "invalid token" == json_data["text"]

def test_DELETE_user_expired_token(client):
    token_package = {"username":"user","email":"user@user.com", "exp": datetime.utcnow() - timedelta(seconds=30)}
    token = jwt.encode(token_package, app.app.config["SECRET_KEY"], algorithm="HS256")
    rv = client.delete("/api/users", json={"token":token.decode("utf-8")})
    json_data = rv.get_json()
    assert "expired token" == json_data["text"]

def test_DELETE_user_missing_username_or_email(client):
    token_package = {"username":"user", "exp": datetime.utcnow() + timedelta(seconds=30)}
    token = jwt.encode(token_package, app.app.config["SECRET_KEY"], algorithm="HS256")
    rv = client.delete("/api/users", json={"token":token.decode("utf-8")})
    json_data = rv.get_json()
    assert "invalid token" == json_data["text"]

def test_DELETE_user_invalid_username_or_email(client):
    token_package = {"username":"user","email":"user@user.com", "exp": datetime.utcnow() + timedelta(seconds=30)}
    token = jwt.encode(token_package, app.app.config["SECRET_KEY"], algorithm="HS256")
    rv = client.delete("/api/users", json={"token":token.decode("utf-8")})
    json_data = rv.get_json()
    assert "invalid token" == json_data["text"]

def test_DELETE_user(client):
    token_call = client.get("/api/users", json={"username":"John", "password": "Passw0rd!"})
    token=token_call.get_json()["token"]
    rv = client.delete("/api/users", json={"token":token})
    json_data = rv.get_json()
    assert "John" == json_data["username"]