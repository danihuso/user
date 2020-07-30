from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from password_strength import PasswordPolicy
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Added as suggested by pytest warnings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

def init_db():
    """Wrapper function to initialise the database, necessary for testing"""
    db.create_all()

@app.cli.command('initdb')
def initdb_command():
    """Wrapper funtion to register the CLI initdb command for the FLASK app"""
    init_db()
    print('Initialized the database.')

class User(db.Model):
    """Main database User model using the SQLAlchemy syntax with fields """
    __tablename__ = 'users'
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

    def check_password(self, password):
        """check the password strength"""
        """ With length of at least 8 characters, 1 upper case, 1number, and 1 special character"""
        policy = PasswordPolicy.from_names(length=8,uppercase=1,numbers=1,special=1)
        return len(policy.test(password)) == 0
