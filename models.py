from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    height = db.Column(db.Float)
    birthdate = db.Column(db.Date)
    gender = db.Column(db.String(10))
    goal_weight = db.Column(db.Float)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer)
    content = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime)