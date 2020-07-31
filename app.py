from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from password_strength import PasswordPolicy
from passlib.hash import pbkdf2_sha256
import jwt
import re

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #Added as suggested by pytest warnings
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SECRET_KEY"]="092cfbfe1fb34568b1899802d2af3309"
db = SQLAlchemy(app)

def init_db():
    """Wrapper function to initialise the database, necessary for testing"""
    db.create_all()

@app.cli.command("initdb")
def initdb_command():
    """Wrapper funtion to register the CLI initdb command for the FLASK app"""
    init_db()
    print("Initialized the database.")

class User(db.Model):
    """Main database User model using the SQLAlchemy syntax with fields """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128))
    date_created = db.Column(db.DateTime, default=datetime.now)

    def set_hash_password(self, password):
        """sets the user model password_hash based on password encryption"""
        self.password_hash = pbkdf2_sha256.hash(password)

    def authentificate(self, password):
        """check that the encrypted password matches the User stored password_hash"""
        return pbkdf2_sha256.verify(password, self.password_hash)

@app.route("/api/users", methods = ["POST"])
def new_user():

    def check_password(password):
        """check the password strength"""
        policy = PasswordPolicy.from_names(length=8,uppercase=1,numbers=1,special=1)
        return len(policy.test(password)) == 0

    def validate_email(email):
        """checks if email is a valid string with regular expression"""
        regex = re.compile(r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$")  
        return bool(regex.match(email))

    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")

    if username is None or password is None or email is None:
        return jsonify(error=404, text="missing parameter"), 404
    if User.query.filter_by(username = username).first() is not None:
        return jsonify(error=404, text="user already exist"), 404
    if check_password(password) == False:
        return jsonify(error=404, text="Password should be at least 8 characters with 1 Uppercase, 1 number, and and 1 special character"), 404
    if validate_email(email) == False:
        return jsonify(error=404, text="Please use a valid email"), 404

    user = User(username = username, email=email)
    user.set_hash_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({ "date": user.date_created }), 201

@app.route("/api/users", methods = ["GET"])
def get_token():

    username = request.json.get("username")
    password = request.json.get("password")

    if username is None or password is None:
        return jsonify(error=404, text="missing parameter"), 404
    if User.query.filter_by(username = username).first() is None:
        return jsonify(error=404, text="login incorrect"), 404
    if User.query.filter_by(username=username).first().authentificate(password) == False:
        return jsonify(error=404, text="login incorrect"), 404

    user = User.query.filter_by(username=username).first()
    token_package = {"username":user.username,"email":user.email, "exp": datetime.utcnow() + timedelta(seconds=30)}
    token = jwt.encode(token_package, app.config["SECRET_KEY"], algorithm="HS256")

    return jsonify({ "token":token.decode("utf-8") }), 201