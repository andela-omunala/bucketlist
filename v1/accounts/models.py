import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from flask import g
from sqlalchemy import Integer, String
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from werkzeug.security import generate_password_hash, check_password_hash
from v1.api.models import BucketList
from db_setup import app, db


class User(db.Model):
    """Model for users"""
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String, unique=True)
    email = db.Column(String, unique=True)
    password = db.Column(String)
    bucketlists = db.relationship(
        BucketList, backref='users', cascade="all,delete", lazy='dynamic')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def hash_password(self, new_password):
        """Hashes provided password"""
        self.password = generate_password_hash(new_password)

    def verify_password(self, current_password):
        """Verifies provided password"""
        return check_password_hash(self.password, current_password)

    def generate_token(self, expiration=int(os.getenv('EXPIRE'))):
        """Generates authorization token for a user"""
        serializer = Serializer(app.config['SECRET_KEY'],
                                expires_in=expiration)
        return serializer.dumps({'id': self.id})


def verify_auth_token(token):
    """Verifies provided authorization token"""
    serializer = Serializer(app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token)
    except SignatureExpired:
        return None
    except BadSignature:
        return None
    g.user = db.session.query(User).filter_by(id=data['id']).first()
    return g.user
