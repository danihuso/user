from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from password_strength import PasswordPolicy
from passlib.hash import pbkdf2_sha256
from flask_cors import CORS
import logging
import jwt
import sys
import re
import random
import string

app = Flask(__name__, template_folder = 'templates')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False #Added as suggested by pytest warnings
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SECRET_KEY"]="092cfbfe1fb34568b1899802d2af3309" #Random generate key

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

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

@app.route('/', methods = ["GET"])
def home():
    #Returns the landing page
    #return render_template('home.html')
    return app.send_static_file('index.html')

@app.route("/api/userslist", methods = ["GET"])
def get_users():
    users = User.query.all()
    userList=[]
    for user in users:
        userDetail={
            "username":user.username,
            "email":user.email,
            "created":user.date_created
        }
        userList.append(userDetail)
    return jsonify(userList), 201

@app.route("/api/randompassword", methods = ["POST"])
def get_random_password():

    length = request.json.get("length")

    random_source = string.ascii_letters + string.digits + string.punctuation
    password = random.choice(string.ascii_lowercase)
    password += random.choice(string.ascii_uppercase)
    password += random.choice(string.digits)
    password += random.choice(string.punctuation)

    for i in range(length-4):
        password += random.choice(random_source)

    password_list = list(password)
    random.SystemRandom().shuffle(password_list)
    password = ''.join(password_list)
    return jsonify({"password":password}), 201

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


@app.route("/api/users", methods = ["DELETE"])
def delete_user():
    token = request.json.get("token")
    if token is None:
        return jsonify(error=404, text="missing parameter"), 404
    try:
        payload = jwt.decode(token, app.config.get("SECRET_KEY"), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify(error=404, text="expired token"), 404
    except jwt.InvalidTokenError:
        return jsonify(error=404, text="invalid token"), 404
    if not("username" in payload) or not("email" in payload):
        return jsonify(error=404, text="invalid token"), 404
    user = User.query.filter_by(username=payload["username"]).filter_by(email=payload["email"]).first()
    if user is None:
        return jsonify(error=404, text="invalid token"), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({ "username":user.username }), 201


if __name__ == '__main__':

    logging.basicConfig(stream=sys.stdout,level=logging.WARNING)
    app.run(host='0.0.0.0', port='5000', debug=True)
